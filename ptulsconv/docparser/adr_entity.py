from .doc_entity import SessionDescriptor, TrackDescriptor, TrackClipDescriptor
from .tag_compiler import Event
from typing import Optional, Generator

# field_map maps tags in the text export to fields in FMPXMLRESULT
#  - tuple field 0 is a list of tags, the first tag with contents will be used as source
#  - tuple field 1 is the field in FMPXMLRESULT
#  - tuple field 2 the constructor/type of the field
from .tag_mapping import TagMapping

adr_field_map = ((['Title', 'PT.Session.Name'], 'Title', str),
                 (['Supv'], 'Supervisor', str),
                 (['Client'], 'Client', str),
                 (['Sc'], 'Scene', str),
                 (['Ver'], 'Version', str),
                 (['Reel'], 'Reel', str),
                 (['PT.Clip.Start'], 'Start', str),
                 (['PT.Clip.Finish'], 'Finish', str),
                 (['PT.Clip.Start_Seconds'], 'Start Seconds', float),
                 (['PT.Clip.Finish_Seconds'], 'Finish Seconds', float),
                 (['PT.Clip.Start_Frames'], 'Start Frames', int),
                 (['PT.Clip.Finish_Frames'], 'Finish Frames', int),
                 (['P'], 'Priority', int),
                 (['QN'], 'Cue Number', str),
                 (['Char', 'PT.Track.Name'], 'Character Name', str),
                 (['Actor'], 'Actor Name', str),
                 (['CN'], 'Character Number', str),
                 (['R'], 'Reason', str),
                 (['Rq'], 'Requested by', str),
                 (['Spot'], 'Spot', str),
                 (['PT.Clip.Name', 'Line'], 'Line', str),
                 (['Shot'], 'Shot', str),
                 (['Note'], 'Note', str),
                 (['Mins'], 'Time Budget Mins', float),
                 (['EFF'], 'Effort', str),
                 (['TV'], 'TV', str),
                 (['TBW'], 'To Be Written', str),
                 (['OMIT'], 'Omit', str),
                 (['ADLIB'], 'Adlib', str),
                 (['OPT'], 'Optional', str),
                 (['DONE'], 'Done', str),
                 (['Movie.Filename'], 'Movie', str),
                 (['Movie.Start_Offset_Seconds'], 'Movie Seconds', float),
                 )


class ADRLine:
    title: str
    supervisor: str
    client: str
    scene: str
    version: str
    reel: str
    start: str
    finish: str
    priority: int
    cue_number: str
    character_id: str
    character_name: str
    actor_name: str
    prompt: str
    reason: str
    requested_by: str
    time_budget_mins: float
    note: str
    spot: str
    shot: str
    effort: bool
    tv: bool
    tbw: bool
    omitted: bool
    adlib: bool
    optional: bool

    adr_tag_to_line_map = [
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
    def from_event(cls, event: Event) -> Optional['ADRLine']:
        new = cls()
        TagMapping.apply_rules(cls.adr_tag_to_line_map, event.tags,
                               event.clip_name, event.track_name, event.session_name, new)
        return new

