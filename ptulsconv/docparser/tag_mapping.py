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
