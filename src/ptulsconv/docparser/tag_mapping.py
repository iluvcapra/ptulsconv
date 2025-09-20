import sys
from enum import Enum
from typing import Optional, Callable, Any, List


class TagMapping:
    class ContentSource(Enum):
        Session = 1,
        Track = 2,
        Clip = 3,

    source: str
    alternate_source: Optional[ContentSource]
    formatter: Callable[[str], Any]

    @staticmethod
    def print_rules(for_type: object, output=sys.stdout):
        format_str = "%-20s |  %-20s | %-25s"
        hr = "%s+%s+%s" % ("-" * 21, "-" * 23, "-" * 26)
        print("Tag mapping for %s" % for_type.__name__)
        print(hr)
        print(format_str % ("Tag Source", "Target", "Type"),
              file=output)
        print(hr)
        for rule in for_type.tag_mapping:
            t = for_type.__annotations__[rule.target]
            print(format_str % (rule.source, rule.target, t),
                  file=output)
            if rule.alternate_source is TagMapping.ContentSource.Session:
                print(format_str % (" - (Session Name)", rule.target, t),
                      file=output)
            elif rule.alternate_source is TagMapping.ContentSource.Track:
                print(format_str % (" - (Track Name)", rule.target, t),
                      file=output)
            elif rule.alternate_source is TagMapping.ContentSource.Clip:
                print(format_str % (" - (Clip Name)", rule.target, t),
                      file=output)

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
            if rule.apply(tags, clip_content, track_content, session_content,
                          to):
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

        new_value = None

        if self.source in tags.keys():
            new_value = tags[self.source]
        elif self.alternate_source == TagMapping.ContentSource.Session:
            new_value = session_content
        elif self.alternate_source == TagMapping.ContentSource.Track:
            new_value = track_content
        elif self.alternate_source == TagMapping.ContentSource.Clip:
            new_value = clip_content

        if new_value is not None:
            setattr(to, self.target, self.formatter(new_value))
            return True
        else:
            return False
