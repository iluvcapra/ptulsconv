from ptulsconv.docparser.tag_compiler import Event
from typing import Optional, List, Tuple, Any
from dataclasses import dataclass
from fractions import Fraction

from ptulsconv.docparser.tag_mapping import TagMapping


def make_entities(from_events: List[Event]) -> Tuple[List['GenericEvent'], List['ADRLine']]:
    generic_events = list()
    adr_lines = list()

    for event in from_events:
        result: Any = make_entity(event)
        if type(result) is ADRLine:
            result: ADRLine
            adr_lines.append(result)
        elif type(result) is GenericEvent:
            result: GenericEvent
            generic_events.append(result)

    return generic_events, adr_lines


def make_entity(from_event: Event) -> Optional[object]:
    instance = GenericEvent
    tag_map = GenericEvent.tag_mapping
    if 'QN' in from_event.tags.keys():
        instance = ADRLine
        tag_map += ADRLine.tag_mapping

    new = instance()
    TagMapping.apply_rules(tag_map, from_event.tags,
                           from_event.clip_name, from_event.track_name,
                           from_event.session_name, new)

    new.start = from_event.start
    new.finish = from_event.finish
    return new


@dataclass
class GenericEvent:
    title: Optional[str]
    supervisor: Optional[str]
    client: Optional[str]
    scene: Optional[str]
    version: Optional[str]
    reel: Optional[str]
    start: Optional[Fraction]
    finish: Optional[Fraction]
    omitted: bool
    note: Optional[str]
    requested_by: Optional[str]

    tag_mapping = [
        TagMapping(source='Title', target="title", alt=TagMapping.ContentSource.Session),
        TagMapping(source="Supv", target="supervisor"),
        TagMapping(source="Client", target="client"),
        TagMapping(source="Sc", target="scene"),
        TagMapping(source="Ver", target="version"),
        TagMapping(source="Reel", target="reel"),
        TagMapping(source="Note", target="note"),
        TagMapping(source="Rq", target="requested_by"),
        TagMapping(source="OMIT", target="omitted",
                   formatter=(lambda x: len(x) > 0)),
    ]


@dataclass
class ADRLine(GenericEvent):
    priority: Optional[int]
    cue_number: Optional[str]
    character_id: Optional[str]
    character_name: Optional[str]
    actor_name: Optional[str]
    prompt: Optional[str]
    reason: Optional[str]
    time_budget_mins: Optional[float]
    spot: Optional[str]
    shot: Optional[str]
    effort: bool
    tv: bool
    tbw: bool
    adlib: bool
    optional: bool

    tag_mapping = [

        TagMapping(source="P", target="priority"),
        TagMapping(source="QN", target="cue_number"),
        TagMapping(source="CN", target="character_id"),
        TagMapping(source="Char", target="character_name", alt=TagMapping.ContentSource.Track),
        TagMapping(source="Actor", target="actor_name"),
        TagMapping(source="Line", target="prompt", alt=TagMapping.ContentSource.Clip),
        TagMapping(source="R", target="reason"),
        TagMapping(source="Mins", target="time_budget_mins",
                   formatter=(lambda n: float(n))),
        TagMapping(source="Spot", target="spot"),
        TagMapping(source="Shot", target="shot"),
        TagMapping(source="EFF", target="effort",
                   formatter=(lambda x: len(x) > 0)),
        TagMapping(source="TV", target="tv",
                   formatter=(lambda x: len(x) > 0)),
        TagMapping(source="TBW", target="tbw",
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
