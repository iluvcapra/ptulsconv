from enum import Enum
from typing import Optional, Callable, Any, List, Generator, Tuple
from .doc_entity import SessionDescriptor
from .tagged_string_parser_visitor import parse_tags, TagPreModes
from . import apply_appends
from fractions import Fraction
from collections import namedtuple


class TagCompiler:
    session: SessionDescriptor

    def compile_events(self) -> Generator[Tuple[str, str, str, dict, Fraction, Fraction]]:
        yield from self.apply_tags(
            self.collect_time_spans(
                self.apply_appends(
                    self.parse_data()
                )
            )
        )

    def _marker_tags(self, at):
        retval = dict()
        applicable = [(m, t) for (m, t) in self.session.markers_timed() if t >= at]
        for marker, time in sorted(applicable, key=lambda x: x[1]):
            retval.update(parse_tags(marker.comments).tag_dict)
            retval.update(parse_tags(marker.name).tag_dict)

        return retval

    @staticmethod
    def _coalesce_tags(clip_tags: dict, track_tags: dict,
                       track_comment_tags: dict,
                       timespan_tags: dict,
                       marker_tags: dict, session_tags: dict):

        effective_tags = session_tags
        effective_tags.update(marker_tags)
        effective_tags.update(timespan_tags)
        effective_tags.update(track_comment_tags)
        effective_tags.update(track_tags)
        effective_tags.update(clip_tags)
        return effective_tags

    Intermediate = namedtuple('Intermediate', 'track_content track_tags track_comment_tags '
                                              'clip_content clip_tags clip_tag_mode start finish')

    def parse_data(self) -> Generator[Intermediate]:

        for track, clip, start, finish in self.session.track_clips_timed():
            if clip.state == 'Muted':
                continue

            track_parsed = parse_tags(track.name)
            track_comments_parsed = parse_tags(track.comments)
            clip_parsed = parse_tags(clip.clip_name)

            yield TagCompiler.Intermediate(track_content=track_parsed.content,
                                           track_tags=track_parsed.tag_dict,
                                           track_comment_tags=track_comments_parsed.tag_dict,
                                           clip_content=clip_parsed.content, clip_tags=clip_parsed.tag_dict,
                                           clip_tag_mode=clip_parsed.mode,
                                           start=start, finish=finish)

    @staticmethod
    def apply_appends(parsed: Generator[Intermediate]) -> Generator[Intermediate]:

        def should_append(a, b):
            return b.clip_tag_mode == TagPreModes.APPEND and b.start >= a.finish

        def do_append(a, b):
            merged_tags = a.clip_tags
            merged_tags.update(b.clip_tags)
            return TagCompiler.Intermediate(track_content=a.track_content,
                                            track_tags=a.track_tags,
                                            track_comment_tags=a.track_comment_tags,
                                            clip_content=a.clip_content + ' ' + b.clip_content,
                                            clip_tags=merged_tags, clip_tag_mode=a.clip_tag_mode,
                                            start=a.start, finish=b.finish)

        yield from apply_appends(parsed, should_append, do_append)

    @staticmethod
    def collect_time_spans(parsed: Generator[Intermediate]) -> \
            Generator[Tuple[Intermediate, List[dict, Fraction, Fraction]]]:

        time_spans = list()

        for item in parsed:
            if item.clip_tag_mode == TagPreModes.TIMESPAN:
                time_spans.append((item.clip_tags, item.start, item.finish))
            else:
                yield item, list(time_spans)

    @staticmethod
    def _time_span_tags(at_time: Fraction, applicable_spans) -> dict:
        retval = dict()
        for tags in [a[0] for a in applicable_spans if a.start <= at_time <= a.finish]:
            retval.update(tags)

        return retval

    def apply_tags(self, parsed_with_time_spans) -> Generator[Tuple[str, str, str, dict, Fraction, Fraction]]:

        session_parsed = parse_tags(self.session.header.session_name)

        for event, time_spans in parsed_with_time_spans:
            event: 'TagCompiler.Intermediate'
            marker_tags = self._marker_tags(event.start)
            time_span_tags = self._time_span_tags(event.start, time_spans)
            tags = self._coalesce_tags(clip_tags=event.clip_tags,
                                       track_tags=event.track_tags,
                                       track_comment_tags=event.track_comment_tags,
                                       timespan_tags=time_span_tags,
                                       marker_tags=marker_tags,
                                       session_tags=session_parsed.tag_dict)

            yield event.clip_content, event.track_content, session_parsed.content, tags, event.start, event.finish


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
