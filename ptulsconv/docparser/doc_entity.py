from fractions import Fraction
from ptulsconv.broadcast_timecode import smpte_to_frame_count


class SessionDescriptor:
    def __init__(self, **kwargs):
        self.header = kwargs['header']
        self.files = kwargs['files']
        self.clips = kwargs['clips']
        self.plugins = kwargs['plugins']
        self.tracks = kwargs['tracks']
        self.markers = kwargs['markers']


class HeaderDescriptor:
    def __init__(self, **kwargs):
        self.session_name = kwargs['session_name']
        self.sample_rate = kwargs['sample_rate']
        self.bit_depth = kwargs['bit_depth']
        self.start_timecode = kwargs['start_timecode']
        self.timecode_format = kwargs['timecode_format']
        self.timecode_drop_frame = kwargs['timecode_drop_frame']
        self.count_audio_tracks = kwargs['count_audio_tracks']
        self.count_clips = kwargs['count_clips']
        self.count_files = kwargs['count_files']

    def convert_timecode(self, tc_string) -> Fraction:
        frame_count = smpte_to_frame_count(tc_string,
                                           self.logical_fps,
                                           self.timecode_drop_frame,
                                           include_fractional=False)

        return self.frame_duration * frame_count

    @property
    def start_time(self) -> Fraction:
        """
        The start time of this session.
        :return: Start time in seconds
        """
        return self.convert_timecode(self.start_timecode)

    @property
    def logical_fps(self) -> int:
        return self._get_tcformat_params[0]

    @property
    def frame_duration(self) -> Fraction:
        return self._get_tcformat_params[1]

    @property
    def _get_tcformat_params(self):
        frame_rates = {"23.976": (24, Fraction(1001, 24_000)),
                       "24": (24, Fraction(1, 24)),
                       "29.97": (30, Fraction(1001, 30_000)),
                       "30": (30, Fraction(1, 30)),
                       "59.94": (60, Fraction(1001, 60_000)),
                       "60": (60, Fraction(1, 60))
                       }

        if self.timecode_format in frame_rates.keys():
            return frame_rates[self.timecode_format]
        else:
            raise ValueError("Unrecognized TC rate (%s)" % self.timecode_format)


class TrackDescriptor:
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.comments = kwargs['comments']
        self.user_delay_samples = kwargs['user_delay_samples']
        self.state = kwargs['state']
        self.plugins = kwargs['plugins']
        self.clips = kwargs['clips']


class FileDescriptor(dict):
    pass


class TrackClipDescriptor:
    def __init__(self, **kwargs):
        self.channel = kwargs['channel']
        self.event = kwargs['event']
        self.clip_name = kwargs['clip_name']
        self.start_time = kwargs['start_time']
        self.end_time = kwargs['end_time']
        self.duration = kwargs['duration']
        self.timestamp = kwargs['timestamp']
        self.state = kwargs['state']


class ClipDescriptor(dict):
    pass


class PluginDescriptor(dict):
    pass


class MarkerDescriptor:
    def __init__(self, **kwargs):
        self.number = kwargs['number']
        self.location = kwargs['location']
        self.time_reference = kwargs['time_reference']
        self.units = kwargs['units']
        self.name = kwargs['name']
        self.comments = kwargs['comments']
