from collections import namedtuple
from fractions import Fraction
from typing import Iterator, Tuple, Callable, Generator, Dict, List

import ptulsconv.docparser.doc_entity as doc_entity
from .tagged_string_parser_visitor import parse_tags, TagPreModes

from dataclasses import dataclass


@dataclass
class Event:
    clip_name: str
    track_name: str
    session_name: str
    tags: Dict[str, str]
    start: Fraction
    finish: Fraction


class TagCompiler:
    """
    Uses a `SessionDescriptor` as a data source to produce `Intermediate`
    items.
    """

    Intermediate = namedtuple('Intermediate',
                              'track_content track_tags track_comment_tags '
                              'clip_content clip_tags clip_tag_mode start '
                              'finish')

    session: doc_entity.SessionDescriptor

    def compile_all_time_spans(self) -> List[Tuple[str, str, Fraction,
                                                   Fraction]]:
        """
        :returns: A `List` of (key: str, value: str, start: Fraction,
            finish: Fraction)
        """
        ret_list = list()
        for element in self.parse_data():
            if element.clip_tag_mode == TagPreModes.TIMESPAN:
                for k in element.clip_tags.keys():
                    ret_list.append((k, element.clip_tags[k], element.start,
                                     element.finish))

        return ret_list

    def compile_tag_list(self) -> Dict[str, List[str]]:
        tags_dict = dict()

        def update_tags_dict(other_dict: dict):
            for k in other_dict.keys():
                if k not in tags_dict.keys():
                    tags_dict[k] = set()
                tags_dict[k].add(other_dict[k])

        for parsed in self.parse_data():
            update_tags_dict(parsed.clip_tags)
            update_tags_dict(parsed.track_tags)
            update_tags_dict(parsed.track_comment_tags)

        session_tags = parse_tags(self.session.header.session_name).tag_dict
        update_tags_dict(session_tags)

        for m in self.session.markers:
            marker_tags = parse_tags(m.name).tag_dict
            marker_comment_tags = parse_tags(m.comments).tag_dict
            update_tags_dict(marker_tags)
            update_tags_dict(marker_comment_tags)

        return tags_dict

    def compile_events(self) -> Iterator[Event]:
        step0 = self.parse_data()
        step1 = self.filter_out_directives(step0)
        step2 = self.apply_appends(step1)
        step3 = self.collect_time_spans(step2)
        step4 = self.apply_tags(step3)
        for datum in step4:
            yield Event(clip_name=datum[0], track_name=datum[1],
                        session_name=datum[2], tags=datum[3], start=datum[4],
                        finish=datum[5])

    def _marker_tags(self, at):
        retval = dict()

        applicable = [(m, t) for (m, t) in
                      self.session.markers_timed() if t <= at]

        for marker, _ in sorted(applicable, key=lambda x: x[1]):
            retval.update(parse_tags(marker.comments or "").tag_dict)
            retval.update(parse_tags(marker.name or "").tag_dict)

        return retval

    def filter_out_directives(self,
                              clips: Iterator[Intermediate]) \
            -> Iterator[Intermediate]:
        for clip in clips:
            if clip.clip_tag_mode == 'Directive':
                continue
            else:
                yield clip

    @staticmethod
    def _coalesce_tags(clip_tags: dict, track_tags: dict,
                       track_comment_tags: dict,
                       timespan_tags: dict,
                       marker_tags: dict, session_tags: dict):
        effective_tags = dict()
        effective_tags.update(session_tags)
        effective_tags.update(marker_tags)
        effective_tags.update(timespan_tags)
        effective_tags.update(track_comment_tags)
        effective_tags.update(track_tags)
        effective_tags.update(clip_tags)
        return effective_tags

    def parse_data(self) -> Iterator[Intermediate]:

        for track, clip, start, finish, _ in self.session.track_clips_timed():
            if clip.state == 'Muted':
                continue

            track_parsed = parse_tags(track.name)
            track_comments_parsed = parse_tags(track.comments)
            clip_parsed = parse_tags(clip.clip_name)

            yield TagCompiler.Intermediate(
                track_content=track_parsed.content,
                track_tags=track_parsed.tag_dict,
                track_comment_tags=track_comments_parsed.tag_dict,
                clip_content=clip_parsed.content,
                clip_tags=clip_parsed.tag_dict,
                clip_tag_mode=clip_parsed.mode,
                start=start, finish=finish)

    @staticmethod
    def apply_appends(parsed: Iterator[Intermediate]) -> \
            Iterator[Intermediate]:

        def should_append(a, b):
            return b.clip_tag_mode == TagPreModes.APPEND and \
                b.start >= a.finish

        def do_append(a, b):
            merged_tags = dict(a.clip_tags)
            merged_tags.update(b.clip_tags)
            return TagCompiler.Intermediate(
                track_content=a.track_content,
                track_tags=a.track_tags,
                track_comment_tags=a.track_comment_tags,
                clip_content=a.clip_content + ' ' + b.clip_content,
                clip_tags=merged_tags, clip_tag_mode=a.clip_tag_mode,
                start=a.start, finish=b.finish)

        yield from apply_appends(parsed, should_append, do_append)

    @staticmethod
    def collect_time_spans(parsed: Iterator[Intermediate]) -> \
            Iterator[Tuple[Intermediate, Tuple[dict, Fraction, Fraction]]]:

        time_spans = list()

        for item in parsed:
            if item.clip_tag_mode == TagPreModes.TIMESPAN:
                time_spans.append((item.clip_tags, item.start, item.finish))
            else:
                yield item, list(time_spans)

    @staticmethod
    def _time_span_tags(at_time: Fraction, applicable_spans) -> dict:
        retval = dict()
        for tags in reversed([a[0] for a in applicable_spans
                              if a[1] <= at_time <= a[2]]):
            retval.update(tags)

        return retval

    def apply_tags(self, parsed_with_time_spans) ->\
            Iterator[Tuple[str, str, str, dict, Fraction, Fraction]]:

        session_parsed = parse_tags(self.session.header.session_name)

        for event, time_spans in parsed_with_time_spans:
            event: 'TagCompiler.Intermediate'
            marker_tags = self._marker_tags(event.start)
            time_span_tags = self._time_span_tags(event.start, time_spans)
            tags = self._coalesce_tags(
                    clip_tags=event.clip_tags,
                    track_tags=event.track_tags,
                    track_comment_tags=event.track_comment_tags,
                    timespan_tags=time_span_tags,
                    marker_tags=marker_tags,
                    session_tags=session_parsed.tag_dict)

            yield (event.clip_content, event.track_content,
                   session_parsed.content, tags, event.start, event.finish)


def apply_appends(source: Iterator,
                  should_append: Callable,
                  do_append: Callable) -> Generator:
    """
    :param source:
    :param should_append: Called with two variables a and b, your
                        function should return true if b should be
                        appended to a
    :param do_append: Called with two variables a and b, your function
                        should return
    :returns: A Generator
    """
    this_element = next(source)
    for element in source:
        if should_append(this_element, element):
            this_element = do_append(this_element, element)
        else:
            yield this_element
            this_element = element

    yield this_element
