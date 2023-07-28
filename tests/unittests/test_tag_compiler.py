import unittest

import ptulsconv.docparser.tag_compiler
from ptulsconv.docparser import doc_entity
from fractions import Fraction


class TestTagCompiler(unittest.TestCase):

    def test_one_track(self):
        c = ptulsconv.docparser.tag_compiler.TagCompiler()

        test_session = self.make_test_session()

        c.session = test_session

        events = c.compile_events()
        event1 = next(events)
        self.assertEqual('This is clip 1', event1.clip_name)
        self.assertEqual('Track 1', event1.track_name)
        self.assertEqual('Test Session', event1.session_name)
        self.assertEqual(dict(A='A',
                              Color='Blue',
                              Ver='1.1',
                              Mode='2',
                              Comment='This is some text in the comments',
                              Part='1'), event1.tags)
        self.assertEqual(Fraction(3600, 1), event1.start)

        event2 = next(events)
        self.assertEqual("This is the second clip ...and this is the last clip", event2.clip_name)
        self.assertEqual('Track 1', event2.track_name)
        self.assertEqual('Test Session', event2.session_name)
        self.assertEqual(dict(R='Noise', A='A', B='B',
                              Color='Red',
                              Comment='This is some text in the comments',
                              N='1', Mode='2',
                              Ver='1.1',
                              M1='M1',
                              Part='2'), event2.tags)

        self.assertEqual(c.session.header.convert_timecode('01:00:01:10'), event2.start)
        self.assertEqual(c.session.header.convert_timecode('01:00:03:00'), event2.finish)

        self.assertIsNone(next(events, None))

    def test_tag_list(self):
        session = self.make_test_session()
        c = ptulsconv.docparser.tag_compiler.TagCompiler()
        c.session = session

        all_tags = c.compile_tag_list()

        self.assertTrue(all_tags['Mode'] == {'2', '1'})

    @staticmethod
    def make_test_session():
        test_header = doc_entity.HeaderDescriptor(session_name="Test Session $Ver=1.1",
                                                  sample_rate=48000,
                                                  timecode_format="24",
                                                  timecode_drop_frame=False,
                                                  bit_depth=24,
                                                  start_timecode='00:59:00:00',
                                                  count_audio_tracks=1,
                                                  count_clips=3,
                                                  count_files=0
                                                  )
        test_clips = [
            doc_entity.TrackClipDescriptor(channel=1, event=1,
                                           clip_name='This is clip 1 {Color=Blue} $Mode=2',
                                           start_time='01:00:00:00',
                                           finish_time='01:00:01:03',
                                           duration='00:00:01:03',
                                           state='Unmuted',
                                           timestamp=None),
            doc_entity.TrackClipDescriptor(channel=1, event=2,
                                           clip_name='This is the second clip {R=Noise} [B] $Mode=2',
                                           start_time='01:00:01:10',
                                           finish_time='01:00:02:00',
                                           duration='00:00:00:14',
                                           state='Unmuted',
                                           timestamp=None),
            doc_entity.TrackClipDescriptor(channel=1, event=3,
                                           clip_name='& ...and this is the last clip $N=1 $Mode=2',
                                           start_time='01:00:02:00',
                                           finish_time='01:00:03:00',
                                           duration='00:00:01:00',
                                           state='Unmuted',
                                           timestamp=None),
        ]
        test_track = doc_entity.TrackDescriptor(
            index=0,
            name="Track 1 [A] {Color=Red} $Mode=1",
                                                comments="{Comment=This is some text in the comments}",
                                                user_delay_samples=0,
                                                plugins=[],
                                                state=[],
                                                clips=test_clips)

        markers = [doc_entity.MarkerDescriptor(number=1,
                                               location="01:00:00:00",
                                               time_reference=48000 * 3600,
                                               units="Samples",
                                               name="Marker 1 {Part=1}",
                                               comments=""
                                               ),
                   doc_entity.MarkerDescriptor(number=2,
                                               location="01:00:01:00",
                                               time_reference=48000 * 3601,
                                               units="Samples",
                                               name="Marker 2 {Part=2}",
                                               comments="[M1]"
                                               ),
                   ]

        test_session = doc_entity.SessionDescriptor(header=test_header,
                                                    tracks=[test_track],
                                                    clips=[],
                                                    files=[],
                                                    markers=markers,
                                                    plugins=[])
        return test_session


if __name__ == '__main__':
    unittest.main()
