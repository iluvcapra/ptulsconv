from fractions import Fraction
from ptulsconv.broadcast_timecode import TimecodeFormat
from typing import Tuple, List, Iterator


class SessionDescriptor:
    header: "HeaderDescriptor"
    files: List["FileDescriptor"]
    clips: List["ClipDescriptor"]
    plugins: List["PluginDescriptor"]
    tracks: List["TrackDescriptor"]
    markers: List["MarkerDescriptor"]

    def __init__(self, **kwargs):
        self.header = kwargs['header']
        self.files = kwargs['files']
        self.clips = kwargs['clips']
        self.plugins = kwargs['plugins']
        self.tracks = kwargs['tracks']
        self.markers = kwargs['markers']

    def markers_timed(self) -> Iterator[Tuple['MarkerDescriptor', Fraction]]:
        """
        Iterate each marker in the session with its respective time reference.
        """
        for marker in self.markers:
            marker_time = Fraction(marker.time_reference,
                                   int(self.header.sample_rate))
            # marker_time = self.header.convert_timecode(marker.location)
            yield marker, marker_time

    def tracks_clips(self) -> Iterator[Tuple['TrackDescriptor',
                                             'TrackClipDescriptor']]:
        """
        Iterate each track clip with its respective owning clip.
        """
        for track in self.tracks:
            for clip in track.clips:
                yield track, clip

    def track_clips_timed(self) -> Iterator[Tuple["TrackDescriptor",
                                                  "TrackClipDescriptor",
                                                  Fraction, Fraction, Fraction]
                                            ]:
        """
        Iterate each track clip with its respective owning clip and timing
        information.

        :returns: A Generator that yields track, clip, start time, finish time,
        and timestamp
        """
        for track, clip in self.tracks_clips():
            start_time = self.header.convert_timecode(clip.start_timecode)
            finish_time = self.header.convert_timecode(clip.finish_timecode)
            timestamp_time = self.header.convert_timecode(clip.timestamp) \
                if clip.timestamp is not None else None

            yield track, clip, start_time, finish_time, timestamp_time


class HeaderDescriptor:
    session_name: str
    sample_rate: float
    bit_depth: int
    start_timecode: str
    timecode_fps: str
    timecode_drop_frame: bool
    count_audio_tracks: int
    count_clips: int
    count_files: int

    def __init__(self, **kwargs):
        self.session_name = kwargs['session_name']
        self.sample_rate = kwargs['sample_rate']
        self.bit_depth = kwargs['bit_depth']
        self.start_timecode = kwargs['start_timecode']
        self.timecode_fps = kwargs['timecode_format']
        self.timecode_drop_frame = kwargs['timecode_drop_frame']
        self.count_audio_tracks = kwargs['count_audio_tracks']
        self.count_clips = kwargs['count_clips']
        self.count_files = kwargs['count_files']

    @property
    def timecode_format(self):
        return TimecodeFormat(frame_duration=self.frame_duration,
                              logical_fps=self.logical_fps,
                              drop_frame=self.timecode_drop_frame)

    def convert_timecode(self, tc_string: str) -> Fraction:
        return self.timecode_format.smpte_to_seconds(tc_string)

    @property
    def start_time(self) -> Fraction:
        """
        The start time of this session.
        :return: Start time in seconds
        """
        return self.convert_timecode(self.start_timecode)

    @property
    def logical_fps(self) -> int:
        return self._get_tc_format_params[0]

    @property
    def frame_duration(self) -> Fraction:
        return self._get_tc_format_params[1]

    @property
    def _get_tc_format_params(self) -> Tuple[int, Fraction]:
        frame_rates = {"23.976": (24, Fraction(1001, 24_000)),
                       "24": (24, Fraction(1, 24)),
                       "25": (25, Fraction(1, 25)),
                       "29.97": (30, Fraction(1001, 30_000)),
                       "30": (30, Fraction(1, 30)),
                       "59.94": (60, Fraction(1001, 60_000)),
                       "60": (60, Fraction(1, 60))
                       }

        if self.timecode_fps in frame_rates.keys():
            return frame_rates[self.timecode_fps]
        else:
            raise ValueError("Unrecognized TC rate (%s)" %
                             self.timecode_format)


class TrackDescriptor:
    index: int
    name: str
    comments: str
    user_delay_samples: int
    state: List[str]
    plugins: List[str]
    clips: List["TrackClipDescriptor"]

    def __init__(self, **kwargs):
        self.index = kwargs['index']
        self.name = kwargs['name']
        self.comments = kwargs['comments']
        self.user_delay_samples = kwargs['user_delay_samples']
        self.state = kwargs['state']
        self.plugins = kwargs['plugins']
        self.clips = kwargs['clips']


class FileDescriptor(dict):
    pass


class TrackClipDescriptor:
    channel: int
    event: int
    clip_name: str
    start_timecode: str
    finish_timecode: str
    duration: str
    timestamp: str
    state: str

    def __init__(self, **kwargs):
        self.channel = kwargs['channel']
        self.event = kwargs['event']
        self.clip_name = kwargs['clip_name']
        self.start_timecode = kwargs['start_time']
        self.finish_timecode = kwargs['finish_time']
        self.duration = kwargs['duration']
        self.timestamp = kwargs['timestamp']
        self.state = kwargs['state']


class ClipDescriptor(dict):
    pass


class PluginDescriptor(dict):
    pass


class MarkerDescriptor:
    number: int
    location: str
    time_reference: int
    units: str
    name: str
    comments: str

    def __init__(self, **kwargs):
        self.number = kwargs['number']
        self.location = kwargs['location']
        self.time_reference = kwargs['time_reference']
        self.units = kwargs['units']
        self.name = kwargs['name']
        self.comments = kwargs['comments']
