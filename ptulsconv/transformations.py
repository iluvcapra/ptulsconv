from . import broadcast_timecode
from .docparser.tagged_string_parser_visitor import TaggedStringResult, tag_grammar
from parsimonious.exceptions import IncompleteParseError
import math
import sys

from .docparser.tagged_string_parser_visitor import TagListVisitor
from .reporting import print_advisory_tagging_error, print_section_header_style, print_status_style

from tqdm import tqdm

# fixme this whole file is a mess
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

    def __init__(self, ignore_muted=True, show_progress=False, log_output=sys.stderr):
        self.visitor = TagListVisitor()
        self.ignore_muted = ignore_muted
        self.show_progress = show_progress
        self.log_output = log_output

        self.transformed = list()
        self.timespan_rules = list()
        self.movie_rules = list()
        self.title_tags = None
        self.markers = list()

    def transform(self, input_dict: dict) -> dict:
        self.transformed = list()
        self.timespan_rules = list()
        self.movie_rules = list()

        print_section_header_style('Parsing Tags')

        self.title_tags = self.parse_tags(input_dict['header']['session_name'])
        self.markers = sorted(input_dict['markers'],
                              key=lambda m: m['location_decoded']['frame_count'])

        if self.show_progress:
            track_iter = tqdm(input_dict['tracks'],
                              desc="Reading tracks...", unit='Track')
        else:
            track_iter = input_dict['tracks']

        for track in track_iter:
            if 'Muted' in track['state'] and self.ignore_muted:
                continue

            track_tags = self.parse_tags(track['name'],
                                         parent_track_name=track['name'])
            comment_tags = self.parse_tags(track['comments'],
                                           parent_track_name=track['name'])
            track_context_tags = track_tags.tag_dict
            track_context_tags.update(comment_tags.tag_dict)

            for clip in track['clips']:
                if clip['state'] == 'Muted' and self.ignore_muted:
                    continue

                clip_tags = self.parse_tags(clip['clip_name'],
                                            parent_track_name=track['name'],
                                            clip_time=clip['start_time'])

                if clip_tags.mode == 'Normal':
                    event = self.decorate_event(clip, clip_tags, input_dict['header'],
                                                track_context_tags, track_tags)
                    self.transformed.append(event)

                elif clip_tags.mode == 'Append':
                    assert len(self.transformed) > 0, "First clip is in '&'-Append mode, fatal error."

                    self.transformed[-1].update(clip_tags.tag_dict)
                    self.transformed[-1]['PT.Clip.Name'] = self.transformed[-1]['PT.Clip.Name'] + " " \
                                                           + clip_tags.content
                    self.transformed[-1]['PT.Clip.Finish_Frames'] = clip['end_time_decoded']['frame_count']
                    self.transformed[-1]['PT.Clip.Finish'] = clip['end_time']
                    self.transformed[-1]['PT.Clip.Finish_Seconds'] = \
                        clip['end_time_decoded']['frame_count'] / input_dict['header']['timecode_format']

                elif clip_tags.mode == 'Timespan':
                    rule = {'start_time_literal': clip['start_time'],
                            'start_time': clip['start_time_decoded']['frame_count'],
                            'start_time_seconds': clip['start_time_decoded']['frame_count'] / input_dict['header'][
                                'timecode_format'], 'end_time': clip['end_time_decoded']['frame_count'],
                            'tags': clip_tags.tag_dict}
                    self.timespan_rules.append(rule)

                elif clip_tags.mode == 'Movie':
                    rule = dict(movie_path=clip_tags.tag_dict['Movie'],
                                start_time=clip['start_time_decoded']['frame_count'],
                                end_time=clip['end_time_decoded']['frame_count'])
                    self.movie_rules.append(rule)

        print_status_style('Processed %i clips' % len(self.transformed))
        return dict(header=input_dict['header'], events=self.transformed)

    def decorate_event(self, clip, clip_tags, header_dict, track_context_tags, track_tags):
        event = dict()
        start_frame = clip['start_time_decoded']['frame_count']
        event.update(self.title_tags.tag_dict)
        event.update(track_context_tags)
        event.update(self.effective_timespan_tags_at_time(start_frame))
        event.update(self.effective_marker_tags_at_time(start_frame))
        event.update(self.effective_movie_at_time(start_frame, header_dict['timecode_format']))
        event.update(clip_tags.tag_dict)
        event['PT.Track.Name'] = track_tags.content
        event['PT.Session.Name'] = self.title_tags.content
        event['PT.Session.TimecodeFormat'] = header_dict['timecode_format']
        event['PT.Session.Start'] = header_dict['start_timecode']
        event['PT.Session.DropFrame'] = header_dict['timecode_drop_frame']
        event['PT.Clip.Number'] = clip['event']
        event['PT.Clip.Name'] = clip_tags.content
        event['PT.Clip.Start'] = clip['start_time']
        event['PT.Clip.Finish'] = clip['end_time']
        event['PT.Clip.Start_Frames'] = start_frame
        event['PT.Clip.Finish_Frames'] = clip['end_time_decoded']['frame_count']
        event['PT.Clip.Start_Seconds'] = start_frame / header_dict['timecode_format']
        event['PT.Clip.Finish_Seconds'] = clip['end_time_decoded']['frame_count'] / header_dict['timecode_format']
        return event

    def effective_movie_at_time(self, time, timecode_format) -> dict:
        retval = dict()

        for rule in reversed(self.movie_rules):
            if rule['start_time'] <= time <= rule['end_time']:
                retval['Movie.Filename'] = rule['movie_path']
                retval['Movie.Start_Offset_Frames'] = time - rule['start_time']
                retval['Movie.Start_Offset_Seconds'] = (time - rule['start_time']) / timecode_format
                break

        return retval

    def effective_timespan_tags_at_time(self, time) -> dict:
        retval = dict()

        for rule in self.timespan_rules:
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

    def effective_marker_tags_at_time(self, time):
        retval = dict()

        for marker in self.markers:
            marker_name_tags = self.parse_tags(marker['name'])
            marker_comment_tags = self.parse_tags(marker['comments'])
            effective_tags = marker_name_tags.tag_dict
            effective_tags.update(marker_comment_tags.tag_dict)

            if marker['location_decoded']['frame_count'] <= time:
                retval.update(effective_tags)
            else:
                break
        return retval

    def parse_tags(self, source, parent_track_name=None, clip_time=None) -> TaggedStringResult:
        try:
            parse_tree = tag_grammar.parse(source)
            return self.visitor.visit(parse_tree)
        except IncompleteParseError as e:
            print_advisory_tagging_error(failed_string=source,
                                         parent_track_name=parent_track_name,
                                         clip_time=clip_time, position=e.pos)

            trimmed_source = source[:e.pos]
            parse_tree = tag_grammar.parse(trimmed_source)
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
        offset = 0  # self.start
        offset_sec = 0.  # self.start / input_dict['header']['timecode_format']
        for event in input_dict['events']:
            if self.start <= event['PT.Clip.Start_Frames'] <= self.end:
                e = event
                e['PT.Clip.Start_Frames'] = event['PT.Clip.Start_Frames'] - offset
                e['PT.Clip.Finish_Frames'] = event['PT.Clip.Finish_Frames'] - offset
                e['PT.Clip.Start_Seconds'] = event['PT.Clip.Start_Seconds'] - offset_sec
                e['PT.Clip.Finish_Seconds'] = event['PT.Clip.Finish_Seconds'] - offset_sec
                out_events.append(e)

        return dict(header=input_dict['header'], events=out_events)
