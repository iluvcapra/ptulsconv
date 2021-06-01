from enum import Enum
from typing import Optional, Callable, Any, List
from .doc_entity import SessionDescriptor, TrackClipDescriptor
from .tagged_string_parser_visitor import parse_tags, TagPreModes
from . import apply_appends
from fractions import Fraction


class TagCompiler:
    session: SessionDescriptor


    def timespan_tags(self, at: Fraction, track_index: int):
        retval = dict()
        for this_track_idx, _, clip, start, finish, _ in self.session.track_clips_timed():
            if this_track_idx > track_index:
                break

            clip_parsed = parse_tags(clip)
            if clip_parsed.mode == TagPreModes.TIMESPAN and start <= at < finish:
                retval.update(clip_parsed.tag_dict)

        return retval

    def marker_tags(self, at):
        retval = dict()

        return retval

    def combined_clips(self):

        def should_append(_, rhs):
            parsed = parse_tags(rhs[0][2].clip_name)
            return parsed.mode == TagPreModes.APPEND

        def do_append(lhs: List, rhs: List):
            return lhs + rhs

        source = ([x] for x in self.session.track_clips_timed())
        yield from apply_appends(source, should_append, do_append)

    def coalesce_tags(self, clip_tags: dict, track_tags: dict, timespan_tags: dict,
                      marker_tags: dict, session_tags: dict):

        effective_tags = session_tags
        effective_tags.update(marker_tags)
        effective_tags.update(timespan_tags)
        effective_tags.update(track_tags)
        effective_tags.update(clip_tags)
        return effective_tags

    def compiled_clips(self):
        session_parsed = parse_tags(self.session.header.session_name)
        for track_idx, track, clip, start, finish, _ in self.session.track_clips_timed():
            clip_parsed = parse_tags(clip.clip_name)
            track_parsed = parse_tags(track.name)

            timespan_tags = self.timespan_tags(start, track_idx)
            marker_tags = self.marker_tags(start)

            tags = self.coalesce_tags(clip_parsed.tag_dict, track_parsed.tag_dict,
                                      timespan_tags, marker_tags, session_parsed.tag_dict)

            yield track, clip, tags, start, finish





class TagMapping:

    class ContentSource(Enum):
        Session = 1,
        Track = 2,
        Clip = 3,

    source: str
    alternate_source: Optional[ContentSource]
    formatter: Callable[[str], Any]

    @staticmethod
    def apply_rules(rules: List['TagMapping'],
                    tags: dict,
                    clip_content: str,
                    track_content: str,
                    session_content: str,
                    to: object):

        done = set()
        for rule in rules:
            if rule.target in done:
                continue
            if rule.apply(tags, clip_content, track_content, session_content, to):
                done.update(rule.target)

    def __init__(self, source: str,
                 target: str,
                 alt: Optional[ContentSource] = None,
                 formatter=None):
        self.source = source
        self.target = target
        self.alternate_source = alt
        self.formatter = formatter or (lambda x: x)

    def apply(self, tags: dict,
              clip_content: str,
              track_content: str,
              session_content: str, to: object) -> bool:

        setter = getattr(to, self.target)
        new_value = None

        if self.source in tags.keys():
            new_value = tags[self.source]
        elif self.alternate_source == 1:
            new_value = session_content
        elif self.alternate_source == 2:
            new_value = track_content
        elif self.alternate_source == 3:
            new_value = clip_content

        if new_value is not None:
            setter(self.formatter(new_value))
            return True
        else:
            return False

