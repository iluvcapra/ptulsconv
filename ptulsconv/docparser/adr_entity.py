from ptulsconv.docparser.tag_compiler import Event
from typing import Optional
from dataclasses import dataclass

from ptulsconv.docparser.tag_mapping import TagMapping


@dataclass
class ADRLine:
    title: Optional[str]
    supervisor: Optional[str]
    client: Optional[str]
    scene: Optional[str]
    version: Optional[str]
    reel: Optional[str]
    start: Optional[str]
    finish: Optional[str]
    priority: Optional[int]
    cue_number: Optional[str]
    character_id: Optional[str]
    character_name: Optional[str]
    actor_name: Optional[str]
    prompt: Optional[str]
    reason: Optional[str]
    requested_by: Optional[str]
    time_budget_mins: Optional[float]
    note: Optional[str]
    spot: Optional[str]
    shot: Optional[str]
    effort: bool
    tv: bool
    tbw: bool
    omitted: bool
    adlib: bool
    optional: bool

    tag_mapping = [
        TagMapping(source='Title', target="title", alt=TagMapping.ContentSource.Session),
        TagMapping(source="Supv", target="supervisor"),
        TagMapping(source="Client", target="client"),
        TagMapping(source="Sc", target="scene"),
        TagMapping(source="Ver", target="version"),
        TagMapping(source="Reel", target="reel"),
        TagMapping(source="P", target="priority"),
        TagMapping(source="QN", target="cue_number"),
        TagMapping(source="CN", target="character_id"),
        TagMapping(source="Char", target="character_name", alt=TagMapping.ContentSource.Track),
        TagMapping(source="Actor", target="actor_name"),
        TagMapping(source="Line", target="prompt", alt=TagMapping.ContentSource.Clip),
        TagMapping(source="R", target="reason"),
        TagMapping(source="Rq", target="requested_by"),
        TagMapping(source="Mins", target="time_budget_mins",
                   formatter=(lambda n: float(n))),
        TagMapping(source="Note", target="note"),
        TagMapping(source="Spot", target="spot"),
        TagMapping(source="Shot", target="shot"),
        TagMapping(source="EFF", target="effort",
                   formatter=(lambda x: len(x) > 0)),
        TagMapping(source="TV", target="tv",
                   formatter=(lambda x: len(x) > 0)),
        TagMapping(source="TBW", target="tbw",
                   formatter=(lambda x: len(x) > 0)),
        TagMapping(source="OMIT", target="omitted",
                   formatter=(lambda x: len(x) > 0)),
        TagMapping(source="ADLIB", target="adlib",
                   formatter=(lambda x: len(x) > 0)),
        TagMapping(source="OPT", target="optional",
                   formatter=(lambda x: len(x) > 0))
    ]

    def __init__(self):
        self.title = None
        self.supervisor = None
        self.client = None
        self.scene = None
        self.version = None
        self.reel = None
        self.start = None
        self.finish = None
        self.priority = None
        self.cue_number = None
        self.character_id = None
        self.character_name = None
        self.actor_name = None
        self.prompt = None
        self.reason = None
        self.requested_by = None
        self.time_budget_mins = None
        self.note = None
        self.spot = None
        self.shot = None
        self.effort = False
        self.tv = False
        self.tbw = False
        self.omitted = False
        self.adlib = False
        self.optional = False

    @classmethod
    def from_event(cls, event: Event) -> 'ADRLine':
        new = cls()
        TagMapping.apply_rules(cls.tag_mapping, event.tags,
                               event.clip_name, event.track_name, event.session_name, new)
        return new


