from . import broadcast_timecode
import math

class Transformation:
    def transform(self, input_dict) -> dict:
        return input_dict


class TimecodeInterpreter(Transformation):

    def __init__(self):
        self.apply_session_start = False

    def transform(self, input_dict: dict) -> dict:
        retval = super().transform(input_dict)
        rate = input_dict['header']['timecode_format']
        start_tc = self.convert_time(input_dict['header']['start_timecode'], rate,
                                     drop_frame=input_dict['header']['timecode_drop_frame'])

        retval['header']['start_timecode_decoded'] = start_tc
        retval['tracks'] = self.convert_tracks(input_dict['tracks'], timecode_rate=rate,
                                               drop_frame=retval['header']['timecode_drop_frame'])


        for marker in retval['markers']:
            marker['location_decoded'] = self.convert_time(marker['location'], rate,
                                                           drop_frame=retval['header']['timecode_drop_frame'])

        return retval

    def convert_tracks(self, tracks, timecode_rate, drop_frame):
        for track in tracks:
            new_clips = []
            for clip in track['clips']:
                new_clips.append( self.convert_clip(clip, drop_frame=drop_frame, timecode_rate= timecode_rate) )

            track['clips'] = new_clips

        return tracks

    def convert_clip(self, clip, timecode_rate, drop_frame):
        time_fields = ['start_time', 'end_time', 'duration', 'timestamp']

        for time_field in time_fields:
            if clip[time_field] is not None:
                clip[time_field + "_decoded"] = self.convert_time(clip[time_field], drop_frame=drop_frame,
                                                                  frame_rate=timecode_rate)
        return clip

    def convert_time(self, time_string, frame_rate, drop_frame=False):
        lfps = math.ceil(frame_rate)

        frame_count = broadcast_timecode.smpte_to_frame_count(time_string, lfps, drop_frame_hint=drop_frame)

        return dict(frame_count=frame_count, logical_fps=lfps, drop_frame=drop_frame)


