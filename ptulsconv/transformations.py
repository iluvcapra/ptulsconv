from . import broadcast_timecode
from parsimonious import Grammar, NodeVisitor
from parsimonious.exceptions import IncompleteParseError
import math
import sys
from .reporting import print_advisory_tagging_error, print_section_header_style, print_status_style

from tqdm import tqdm


class Transformation:
    def transform(self, input_dict) -> dict:
        return input_dict


class TimecodeInterpreter(Transformation):

    def __init__(self):
        self.apply_session_start = False

    def transform(self, input_dict: dict) -> dict:
        print_section_header_style('Converting Timecodes')

        retval = super().transform(input_dict)
        rate = input_dict['header']['timecode_format']
        start_tc = self.convert_time(input_dict['header']['start_timecode'], rate,
                                     drop_frame=input_dict['header']['timecode_drop_frame'])

        retval['header']['start_timecode_decoded'] = start_tc
        print_status_style('Converted start timecode.')

        retval['tracks'] = self.convert_tracks(input_dict['tracks'], timecode_rate=rate,
                                               drop_frame=retval['header']['timecode_drop_frame'])

        print_status_style('Converted clip timecodes for %i tracks.' % len(retval['tracks']))

        for marker in retval['markers']:
            marker['location_decoded'] = self.convert_time(marker['location'], rate,
                                                           drop_frame=retval['header']['timecode_drop_frame'])

        print_status_style('Converted %i markers.' % len(retval['markers']))

        return retval

    def convert_tracks(self, tracks, timecode_rate, drop_frame):
        for track in tracks:
            new_clips = []
            for clip in track['clips']:
                new_clips.append(self.convert_clip(clip, drop_frame=drop_frame, timecode_rate=timecode_rate))

            track['clips'] = new_clips

        return tracks

    def convert_clip(self, clip, timecode_rate, drop_frame):
        time_fields = ['start_time', 'end_time', 'duration', 'timestamp']

        for time_field in time_fields:
            if clip[time_field] is not None:
                clip[time_field + "_decoded"] = self.convert_time(clip[time_field], drop_frame=drop_frame,
                                                                  frame_rate=timecode_rate)
        return clip

    def convert_time(self, time_string, frame_rate, drop_frame=False):
        lfps = math.ceil(frame_rate)

        frame_count = broadcast_timecode.smpte_to_frame_count(time_string, lfps, drop_frame_hint=drop_frame)

        return dict(frame_count=frame_count, logical_fps=lfps, drop_frame=drop_frame)


class TagInterpreter(Transformation):
    tag_grammar = Grammar(
        r"""
        document  = modifier? line? word_sep? tag_list?
        line      = word (word_sep word)*
        tag_list  = tag*
        tag       = key_tag / short_tag / full_text_tag / tag_junk
        key_tag        = "[" key "]" word_sep?
        short_tag      = "$" key "=" word word_sep?
        full_text_tag  = "{" key "=" value "}" word_sep?
        key            = ~"[A-Za-z][A-Za-z0-9_]*"
        value          = ~"[^}]+"
        tag_junk       = word word_sep?
        word           = ~"[^ \[\{\$][^ ]*"
        word_sep       = ~" +"
        modifier       = ("@" / "&") word_sep?
        """
    )

    class TagListVisitor(NodeVisitor):
        def visit_document(self, _, visited_children):
            modifier_opt, line_opt, _, tag_list_opt = visited_children

            return dict(line=next(iter(line_opt), None),
                        tags=next(iter(tag_list_opt), None),
                        mode=next(iter(modifier_opt), 'Normal')
                        )

        def visit_line(self, node, _):
            return str.strip(node.text, " ")

        def visit_modifier(self, node, _):
            if node.text.startswith('@'):
                return 'Timespan'
            elif node.text.startswith('&'):
                return 'Append'
            else:
                return 'Normal'

        def visit_tag_list(self, _, visited_children):
            retdict = dict()
            for child in visited_children:
                if child[0] is not None:
                    k, v = child[0]
                    retdict[k] = v
            return retdict

        def visit_key_tag(self, _, children):
            return children[1].text, children[1].text

        def visit_short_tag(self, _, children):
            return children[1].text, children[3].text

        def visit_full_text_tag(self, _, children):
            return children[1].text, children[3].text

        def visit_tag_junk(self, node, _):
            return None

        def generic_visit(self, node, visited_children):
            return visited_children or node

    def __init__(self, ignore_muted=True, show_progress=False, log_output=sys.stderr):
        self.visitor = TagInterpreter.TagListVisitor()
        self.ignore_muted = ignore_muted
        self.show_progress = show_progress
        self.log_output = log_output

    def transform(self, input_dict: dict) -> dict:
        transformed = list()
        timespan_rules = list()

        print_section_header_style('Parsing Tags')

        title_tags = self.parse_tags(input_dict['header']['session_name'])
        markers = sorted(input_dict['markers'], key=lambda m: m['location_decoded']['frame_count'])

        if self.show_progress:
            track_iter = tqdm(input_dict['tracks'], desc="Reading tracks...", unit='Track')
        else:
            track_iter = input_dict['tracks']

        for track in track_iter:
            if 'Muted' in track['state'] and self.ignore_muted:
                continue

            track_tags = self.parse_tags(track['name'], parent_track_name=track['name'])
            comment_tags = self.parse_tags(track['comments'], parent_track_name=track['name'])
            track_context_tags = track_tags['tags']
            track_context_tags.update(comment_tags['tags'])

            for clip in track['clips']:
                if clip['state'] == 'Muted' and self.ignore_muted:
                    continue

                clip_tags = self.parse_tags(clip['clip_name'], parent_track_name=track['name'],
                                            clip_time=clip['start_time'])
                clip_start = clip['start_time_decoded']['frame_count']
                if clip_tags['mode'] == 'Normal':
                    event = dict()
                    event.update(title_tags['tags'])
                    event.update(track_context_tags)
                    event.update(self.effective_timespan_tags_at_time(timespan_rules, clip_start))
                    event.update(self.effective_marker_tags_at_time(markers, clip_start))

                    event.update(clip_tags['tags'])

                    event['PT.Track.Name'] = track_tags['line']
                    event['PT.Session.Name'] = title_tags['line']
                    event['PT.Session.TimecodeFormat'] = input_dict['header']['timecode_format']
                    event['PT.Clip.Number'] = clip['event']
                    event['PT.Clip.Name'] = clip_tags['line']
                    event['PT.Clip.Start'] = clip['start_time']
                    event['PT.Clip.Finish'] = clip['end_time']
                    event['PT.Clip.Start_Frames'] = clip_start
                    event['PT.Clip.Finish_Frames'] = clip['end_time_decoded']['frame_count']
                    event['PT.Clip.Start_Seconds'] = clip_start / input_dict['header']['timecode_format']
                    event['PT.Clip.Finish_Seconds'] = clip['end_time_decoded']['frame_count'] / input_dict['header'][
                        'timecode_format']
                    transformed.append(event)

                elif clip_tags['mode'] == 'Append':
                    assert len(transformed) > 0, "First clip is in '&'-Append mode, fatal error."

                    transformed[-1].update(clip_tags['tags'])
                    transformed[-1]['PT.Clip.Name'] = transformed[-1]['PT.Clip.Name'] + " " + clip_tags['line']
                    transformed[-1]['PT.Clip.Finish_Frames'] = clip['end_time_decoded']['frame_count']
                    transformed[-1]['PT.Clip.Finish'] = clip['end_time']
                    transformed[-1]['PT.Clip.Finish_Seconds'] = clip['end_time_decoded']['frame_count'] / \
                                                                input_dict['header']['timecode_format']


                elif clip_tags['mode'] == 'Timespan':
                    rule = dict(start_time_literal=clip['start_time'],
                                start_time=clip_start,
                                start_time_seconds=clip_start / input_dict['header']['timecode_format'],
                                end_time=clip['end_time_decoded']['frame_count'],
                                tags=clip_tags['tags'])
                    timespan_rules.append(rule)

        print_status_style('Processed %i clips' % len(transformed))
        return dict(header=input_dict['header'], events=transformed)

    def effective_timespan_tags_at_time(_, rules, time) -> dict:
        retval = dict()

        for rule in rules:
            if rule['start_time'] <= time <= rule['end_time']:
                tag_keys = list(rule['tags'].keys())
                tag_times = dict()
                for key in tag_keys:
                    key: str
                    time_value = rule['start_time']
                    tag_times["Timespan." + key + ".Start_Frames"] = time_value
                    tag_times["Timespan." + key + ".Start"] = rule['start_time_literal']
                    tag_times["Timespan." + key + ".Start_Seconds"] = rule['start_time_seconds']

                retval.update(rule['tags'])
                retval.update(tag_times)

        return retval

    def effective_marker_tags_at_time(self, markers, time):
        retval = dict()

        for marker in markers:
            marker_name_tags = self.parse_tags(marker['name'], marker_index=marker['number'])
            marker_comment_tags = self.parse_tags(marker['comments'], marker_index=marker['number'])
            effective_tags = marker_name_tags['tags']
            effective_tags.update(marker_comment_tags['tags'])

            if marker['location_decoded']['frame_count'] <= time:
                retval.update(effective_tags)
            else:
                break
        return retval

    def parse_tags(self, source, parent_track_name=None, clip_time=None, marker_index=None):
        try:
            parse_tree = self.tag_grammar.parse(source)
            return self.visitor.visit(parse_tree)
        except IncompleteParseError as e:
            print_advisory_tagging_error(failed_string=source,
                                         parent_track_name=parent_track_name,
                                         clip_time=clip_time, position=e.pos)

            trimmed_source = source[:e.pos]
            parse_tree = self.tag_grammar.parse(trimmed_source)
            return self.visitor.visit(parse_tree)


class SelectReel(Transformation):

    def __init__(self, reel_num):
        self.reel_num = reel_num

    def transform(self, input_dict) -> dict:
        out_events = []
        for event in input_dict['events']:
            if event['Reel'] == str(self.reel_num):
                offset = event.get('Timespan.Reel.Start_Frames', 0)
                offset_sec = event.get('Timespan.Reel.Start_Seconds', 0.)
                event['PT.Clip.Start_Frames'] -= offset
                event['PT.Clip.Finish_Frames'] -= offset
                event['PT.Clip.Start_Seconds'] -= offset_sec
                event['PT.Clip.Finish_Seconds'] -= offset_sec
                out_events.append(event)

        return dict(header=input_dict['header'], events=out_events)


class SubclipOfSequence(Transformation):

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def transform(self, input_dict: dict) -> dict:
        out_events = []
        offset = 0 #self.start
        offset_sec = 0. #self.start / input_dict['header']['timecode_format']
        for event in input_dict['events']:
            if self.start <= event['PT.Clip.Start_Frames'] <= self.end:
                e = event
                e['PT.Clip.Start_Frames'] = event['PT.Clip.Start_Frames'] - offset
                e['PT.Clip.Finish_Frames'] = event['PT.Clip.Finish_Frames'] - offset
                e['PT.Clip.Start_Seconds'] = event['PT.Clip.Start_Seconds'] - offset_sec
                e['PT.Clip.Finish_Seconds'] = event['PT.Clip.Finish_Seconds'] - offset_sec
                out_events.append(e)

        return dict(header=input_dict['header'], events=out_events)
