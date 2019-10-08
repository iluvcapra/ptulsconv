from . import broadcast_timecode
from parsimonious import Grammar, NodeVisitor
import math

class Transformation:
    def transform(self, input_dict) -> dict:
        return input_dict


class TimecodeInterpreter(Transformation):

    def __init__(self):
        self.apply_session_start = False

    def transform(self, input_dict: dict) -> dict:
        retval = super().transform(input_dict)
        rate = input_dict['header']['timecode_format']
        start_tc = self.convert_time(input_dict['header']['start_timecode'], rate,
                                     drop_frame=input_dict['header']['timecode_drop_frame'])

        retval['header']['start_timecode_decoded'] = start_tc
        retval['tracks'] = self.convert_tracks(input_dict['tracks'], timecode_rate=rate,
                                               drop_frame=retval['header']['timecode_drop_frame'])


        for marker in retval['markers']:
            marker['location_decoded'] = self.convert_time(marker['location'], rate,
                                                           drop_frame=retval['header']['timecode_drop_frame'])

        return retval

    def convert_tracks(self, tracks, timecode_rate, drop_frame):
        for track in tracks:
            new_clips = []
            for clip in track['clips']:
                new_clips.append( self.convert_clip(clip, drop_frame=drop_frame, timecode_rate= timecode_rate) )

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


class TagInterpreter:
    tag_grammar = Grammar(
        r"""
        document  = modifier? line? word_sep? tag_list?
        line      = word (word_sep word)*
        tag_list  = tag*
        tag       = key_tag / short_tag / full_text_tag / tag_junk
        key_tag        = "[" key "]" word_sep?
        short_tag      = "$" key "=" word 
        full_text_tag  = "{" key "=" value "}" word_sep?
        key            = ~"[A-Za-z][A-Za-z0-9_]*"
        value          = ~"[^}]+"
        tag_junk       = (word word_sep)*
        word           = ~"[^ \[\{\$][^ ]*"
        word_sep       = ~" +"
        modifier       = ("@" / "&") word_sep?
        """
    )

    class TagListVisitor(NodeVisitor):
        def visit_document(self, _, visited_children):
            modifier_opt, line_opt, _, tag_list_opt = visited_children

            return dict(line= next(iter(line_opt), None),
                        tags= next(iter(tag_list_opt), None),
                        mode= next(iter(modifier_opt), 'Normal')
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
                k, v = child[0]
                retdict[k] = v
            return retdict

        def visit_key_tag(self, _, children):
            return children[1].text, children[1].text

        def visit_short_tag(self, _, children):
            return children[1].text, children[3].text

        def visit_full_text_tag(self, _, children):
            return children[1].text, children[3].text

        def generic_visit(self, node, visited_children):
            return visited_children or node

    def __init__(self):
        pass

    def parse_tags(self, source):
        parse_tree = self.tag_grammar.parse(source)
        v = TagInterpreter.TagListVisitor()
        return v.visit(parse_tree)



