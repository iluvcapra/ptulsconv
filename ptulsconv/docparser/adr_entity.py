from .doc_entity import SessionDescriptor, TrackDescriptor, TrackClipDescriptor
from typing import Optional, Generator, List, Callable
from tagged_string_parser_visitor import parse_tags
from itertools import chain
from functools import reduce

from fractions import Fraction
# field_map maps tags in the text export to fields in FMPXMLRESULT
#  - tuple field 0 is a list of tags, the first tag with contents will be used as source
#  - tuple field 1 is the field in FMPXMLRESULT
#  - tuple field 2 the constructor/type of the field

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
    prompt: str
    reason: str
    requested_by: str
    note: str
    spot: str
    shot: str
    effort: bool
    tv: bool
    tbw: bool
    omitted: bool
    adlib: bool
    optional: bool
    done: bool

    @staticmethod
    def from_clip(clip: TrackClipDescriptor,
                  track: TrackDescriptor,
                  session: SessionDescriptor) -> Optional['ADRLine']:
        pass

    @staticmethod
    def generate_lines(session: SessionDescriptor) -> Generator['ADRLine']:
        for track in session.tracks:
            for track_clip in track.clips:
                line = ADRLine.from_clip(track_clip, track, session)
                if line is not None:
                    yield line


