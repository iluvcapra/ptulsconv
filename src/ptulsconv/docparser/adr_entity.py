"""
This module defines classes and methods for converting :class:`Event` objects
into :class:`ADRLine` objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from ptulsconv.docparser.tag_compiler import Event
from ptulsconv.docparser.tag_mapping import TagMapping

GENERIC_TAG_MAPPING = [
    TagMapping(source="Title", target="title", alt=TagMapping.ContentSource.Session),
    TagMapping(source="Supv", target="supervisor"),
    TagMapping(source="Client", target="client"),
    TagMapping(source="Sc", target="scene"),
    TagMapping(source="Ver", target="version"),
    TagMapping(source="Reel", target="reel"),
    TagMapping(source="Note", target="note"),
    TagMapping(source="Rq", target="requested_by"),
    TagMapping(source="OMIT", target="omitted", formatter=(lambda x: len(x) > 0)),
]

ADR_TAG_MAPPING = [
    TagMapping(source="P", target="priority"),
    TagMapping(source="QN", target="cue_number"),
    TagMapping(source="CN", target="character_id"),
    TagMapping(
        source="Char", target="character_name", alt=TagMapping.ContentSource.Track
    ),
    TagMapping(source="Actor", target="actor_name"),
    TagMapping(source="Line", target="prompt", alt=TagMapping.ContentSource.Clip),
    TagMapping(source="R", target="reason"),
    TagMapping(
        source="Mins", target="time_budget_mins", formatter=(lambda n: float(n))
    ),
    TagMapping(source="Spot", target="spot"),
    TagMapping(source="Shot", target="shot"),
    TagMapping(source="EFF", target="effort", formatter=(lambda x: len(x) > 0)),
    TagMapping(source="TV", target="tv", formatter=(lambda x: len(x) > 0)),
    TagMapping(source="TBW", target="tbw", formatter=(lambda x: len(x) > 0)),
    TagMapping(source="ADLIB", target="adlib", formatter=(lambda x: len(x) > 0)),
    TagMapping(source="OPT", target="optional", formatter=(lambda x: len(x) > 0)),
]


def make_entities(
    from_events: list[Event],
) -> tuple[list[GenericEvent], list[ADRLine]]:
    """
    Accepts a list of Events and converts them into either ADRLine events or
    GenricEvents by calling :func:`make_entity` on each member.

    :param from_events: A list of `Event` objects.

    :returns: A tuple of two lists, the first containing :class:`GenericEvent`
        and the second containing :class:`ADRLine`.
    """
    generic_events = []
    adr_lines = []

    for event in from_events:
        result = make_entity(event)
        if type(result) is ADRLine:
            adr_lines.append(result)
        elif type(result) is GenericEvent:
            generic_events.append(result)

    return generic_events, adr_lines


def make_entity(from_event: Event) -> object | None:
    """
    Accepts an event and creates either an :class:`ADRLine` or a
    :class:`GenericEvent`. An event is an "ADRLine" if it has a cue number/"QN"
    tag field.

    :param from_event:  An :class:`Event`.

    """
    instance = GenericEvent
    tag_map = GENERIC_TAG_MAPPING
    if "QN" in from_event.tags:
        instance = ADRLine
        tag_map += ADR_TAG_MAPPING

    new = instance()
    TagMapping.apply_rules(
        rules=tag_map,
        tags=from_event.tags,
        clip_content=from_event.clip_name,
        track_content=from_event.track_name,
        session_content=from_event.session_name,
        to=new,
    )

    new.start = from_event.start
    new.finish = from_event.finish
    return new


@dataclass
class GenericEvent:
    title: str = ""
    supervisor: str | None = None
    client: str | None = None
    scene: str | None = None
    version: str | None = None
    reel: str | None = None
    start: Fraction = Fraction(0, 1)
    finish: Fraction = Fraction(0, 1)
    omitted: bool = False
    note: str | None = None
    requested_by: str | None = None


@dataclass
class ADRLine(GenericEvent):
    priority: int | None = None
    cue_number: str | None = None
    character_id: str | None = None
    character_name: str | None = None
    actor_name: str | None = None
    prompt: str | None = None
    reason: str | None = None
    time_budget_mins: float | None = None
    spot: str | None = None
    shot: str | None = None
    effort: bool = False
    tv: bool = False
    tbw: bool = False
    adlib: bool = False
    optional: bool = False
