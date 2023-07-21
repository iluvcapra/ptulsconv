"""
Useful functions for parsing and working with timecode.
"""

import math
import re
from collections import namedtuple
from fractions import Fraction
from typing import Optional, SupportsFloat


class TimecodeFormat(namedtuple("_TimecodeFormat",
                                "frame_duration logical_fps drop_frame")):
    """
    A struct reperesenting a timecode datum.
    """

    def smpte_to_seconds(self, smpte: str) -> Optional[Fraction]:
        frame_count = smpte_to_frame_count(
            smpte, self.logical_fps, drop_frame_hint=self.drop_frame)
        if frame_count is None:
            return None
        else:
            return frame_count * self.frame_duration

    def seconds_to_smpte(self, seconds: SupportsFloat) -> str:
        frame_count = int(seconds / self.frame_duration)
        return frame_count_to_smpte(frame_count, self.logical_fps,
                                    self.drop_frame)


def smpte_to_frame_count(smpte_rep_string: str, frames_per_logical_second: int,
                         drop_frame_hint=False) -> Optional[int]:
    """
    Convert a string with a SMPTE timecode representation into a frame count.

    :param smpte_rep_string: The timecode string
    :param frames_per_logical_second: Num of frames in a logical second. This
        is asserted to be in one of `[24,25,30,48,50,60]`
    :param drop_frame_hint: `True` if the timecode rep is drop frame. This is
        ignored (and implied `True`) if the last separator in the timecode
        string is a semicolon. This is ignored (and implied `False`) if
        `frames_per_logical_second` is not 30 or 60.
    """
    assert frames_per_logical_second in [24, 25, 30, 48, 50, 60]

    m = re.search(
        r'(\d?\d)[:;](\d\d)[:;](\d\d)([:;])(\d\d)(\.\d+)?', smpte_rep_string)

    if m is None:
        return None

    hh, mm, ss, sep, ff, frac = m.groups()
    hh, mm, ss, ff, frac = int(hh), int(
        mm), int(ss), int(ff), float(frac or 0.0)

    drop_frame = drop_frame_hint
    if sep == ";":
        drop_frame = True

    if frames_per_logical_second not in [30, 60]:
        drop_frame = False

    raw_frames = hh * 3600 * frames_per_logical_second + mm * 60 * \
        frames_per_logical_second + ss * frames_per_logical_second + ff

    frames = raw_frames
    if drop_frame is True:
        frames_dropped_per_inst = (frames_per_logical_second / 15)
        mins = hh * 60 + mm
        inst_count = mins - math.floor(mins / 10)
        dropped_frames = int(frames_dropped_per_inst) * inst_count
        frames = raw_frames - dropped_frames

    return frames


def frame_count_to_smpte(frame_count: int, frames_per_logical_second: int,
                         drop_frame: bool = False,
                         fractional_frame: Optional[float] = None) -> str:
    assert frames_per_logical_second in [24, 25, 30, 48, 50, 60]
    assert fractional_frame is None or fractional_frame < 1.0

    nominal_frames = frame_count
    separator = ":"
    if drop_frame:
        assert frames_per_logical_second in [30, 60]
        mins, _ = divmod(nominal_frames, frames_per_logical_second * 60)
        frames_dropped_per_inst = (frames_per_logical_second / 15)
        inst_count = mins - math.floor(mins / 10)
        dropped_frames = frames_dropped_per_inst * inst_count
        nominal_frames = nominal_frames + dropped_frames
        separator = ";"

    hh, rem = divmod(nominal_frames, frames_per_logical_second * 3600)
    mm, rem = divmod(rem, frames_per_logical_second * 60)
    ss, ff = divmod(rem, frames_per_logical_second)

    hh = hh % 24
    if fractional_frame is not None and fractional_frame > 0:
        return "%02i:%02i:%02i%s%02i%s" % (hh, mm, ss, separator, ff,
                                           ("%.3f" % fractional_frame)[1:])
    else:
        return "%02i:%02i:%02i%s%02i" % (hh, mm, ss, separator, ff)


def footage_to_frame_count(footage_string) -> Optional[int]:
    m = re.search(r'(\d+)\+(\d+)(\.\d+)?', footage_string)
    if m is None:
        return None
    feet, frm, frac = m.groups()
    feet, frm, frac = int(feet), int(frm), float(frac or 0.0)

    frames = feet * 16 + frm

    return frames


def frame_count_to_footage(frame_count):
    feet, frm = divmod(frame_count, 16)
    return "%i+%02i" % (feet, frm)
