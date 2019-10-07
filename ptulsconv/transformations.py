from timecode import Timecode, TimecodeError

class Transformation:
    def transform(self, input_dict) -> dict:
        return input_dict


class TimecodeInterpreter(Transformation):

    def __init__(self):
        self.apply_session_start = False

    def transform(self, input_dict: dict) -> dict:
        retval = super().transform(input_dict)
        rate = input_dict['header']['timecode_format']
        start_tc = self.convert_time(input_dict['header']['start_timecode'],
                                                               rate, offset=None)

        retval['header']['start_timecode_decoded'] = start_tc
        convert_start_tc = None
        if self.apply_session_start is True:
            convert_start_tc = Timecode(framerate=input_dict['header']['timecode_format'],
                                        start_timecode=input_dict['header']['start_timecode'])

        retval['tracks'] = self.convert_tracks(input_dict['tracks'], timecode_rate=rate,
                                               session_start=convert_start_tc)


        for marker in retval['markers']:
            marker['location_decoded'] = self.convert_time(marker['location'], rate,
                                                           convert_start_tc)
        return retval

    def convert_tracks(self, tracks, timecode_rate, session_start):
        for track in tracks:
            new_clips = []
            for clip in track['clips']:
                new_clips.append( self.convert_clip( clip ,
                                                     timecode_rate= timecode_rate,
                                                     session_start=session_start ))

            track['clips'] = new_clips
        return tracks

    def convert_clip(self, clip, timecode_rate, session_start):
        time_fields = ['start_time', 'end_time', 'duration', 'timestamp']

        for time_field in time_fields:
            if clip[time_field] is not None:
                if time_field == 'duration':
                    clip[time_field + "_decoded"] = self.convert_time(clip[time_field],
                                                         framerate=timecode_rate, offset=None)
                else:
                    clip[time_field + "_decoded"] = self.convert_time(clip[time_field],
                                                    framerate=timecode_rate, offset=session_start)

        return clip

    def convert_time(self, time_string, framerate, offset= None):
        tc = Timecode(framerate=framerate, start_timecode=time_string)
        if offset is not None:
            tc = tc - offset

        return dict(frames=tc.frames, framrate= framerate, seconds= (float(tc.frames) / float(tc.framerate)))


