import unittest
from ptulsconv import broadcast_timecode
from fractions import Fraction

class TestBroadcastTimecode(unittest.TestCase):
    def test_basic_to_frame_count(self):
        r1 = "01:00:00:00"
        f1 = broadcast_timecode.smpte_to_frame_count(r1, 24, False)
        self.assertEqual(f1, 86_400)
        f2 = broadcast_timecode.smpte_to_frame_count(r1, 30)
        self.assertEqual(f2, 108_000)

        r2 = "0:00:00:01"
        f3 = broadcast_timecode.smpte_to_frame_count(r2, 24)
        self.assertEqual(f3, 1)

    def test_basic_to_string(self):
        c1 = 24
        s1 = broadcast_timecode.frame_count_to_smpte(c1, 24)
        self.assertEqual(s1, "00:00:01:00")
        s2 = broadcast_timecode.frame_count_to_smpte(c1, 30)
        self.assertEqual(s2, "00:00:00:24")
        c2 = 108_000
        s3 = broadcast_timecode.frame_count_to_smpte(c2, 30)
        self.assertEqual(s3, "01:00:00:00")
        c3 = 86401
        s4 = broadcast_timecode.frame_count_to_smpte(c3, 24)
        self.assertEqual(s4, "01:00:00:01")

    def test_drop_frame_to_string(self):
        c1 = 108_000
        s1 = broadcast_timecode.frame_count_to_smpte(c1, 30, drop_frame=True)
        self.assertEqual(s1, "01:00:03;18")

    def test_drop_frame_to_frame_count(self):
        r1 = "01:00:00;00"
        z1 = broadcast_timecode.smpte_to_frame_count(r1, 30, drop_frame_hint=True)
        self.assertEqual(z1, 107_892)

        r11 = "01:00:00;01"
        f11 = broadcast_timecode.smpte_to_frame_count(r11, 30)
        self.assertEqual(f11, 107_893)

        r2 = "00:01:00;02"
        f2 = broadcast_timecode.smpte_to_frame_count(r2, 30, True)
        self.assertEqual(f2, 1800)

        r3 = "00:00:59;29"
        f3 = broadcast_timecode.smpte_to_frame_count(r3, 30, True)
        self.assertEqual(f3, 1799)

    def test_footage_to_frame_count(self):
        s1 = "194+11"
        f1 = broadcast_timecode.footage_to_frame_count(s1)
        self.assertEqual(f1, 3115)

        s3 = "0+0.1"
        f3 = broadcast_timecode.footage_to_frame_count(s3)
        self.assertEqual(f3, 0)

    def test_frame_count_to_footage(self):
        c1 = 19
        s1 = broadcast_timecode.frame_count_to_footage(c1)
        self.assertEqual(s1, "1+03")

    def test_seconds_to_smpte(self):
        secs = Fraction(25, 24)
        frame_duration = Fraction(1, 24)
        tc_format = broadcast_timecode.TimecodeFormat(frame_duration=frame_duration, logical_fps=24, drop_frame=False)
        s1 = tc_format.seconds_to_smpte(secs)
        self.assertEqual(s1, "00:00:01:01")


if __name__ == '__main__':
    unittest.main()
