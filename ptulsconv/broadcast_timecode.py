from fractions import Fraction
import re
import math
import functools


def smpte_to_frame_count(smpte_rep_string: str, frames_per_logical_second: int, drop_frame_hint=False):
    """
    Convert a string with a SMPTE timecode representation into a frame count.

    :param smpte_rep_string: The timecode string
    :param frames_per_logical_second: Num of frames in a logical second. This is asserted to be
            in one of `[24,25,30,48,50,60]`
    :param drop_frame_hint: `True` if the timecode rep is drop frame. This is ignored (and implied `True`) if
            the last separator in the timecode string is a semicolon. This is ignored (and implied `False`) if
            `frames_per_logical_second` is not 30 or 60.
    :returns (frame_count, fraction): If a fractional frame is in the SMPTE string it will be returned here in the
            `fraction` part.
    """
    assert frames_per_logical_second in [24, 25, 30, 48, 50, 60]

    m = re.search("(\d?\d)[:;](\d\d)[:;](\d\d)([:;])(\d\d)(\.\d+)?", smpte_rep_string)
    hh, mm, ss, sep, ff, frac = m.groups()
    hh, mm, ss, ff = int(hh), int(mm), int(ss), int(ff)
    if frac is not None:
        frac = float(frac)

    drop_frame = drop_frame_hint
    if sep == ";":
        drop_frame = True

    if frames_per_logical_second not in [30, 60]:
        drop_frame = False

    raw_frames = hh * 3600 * frames_per_logical_second + mm * 60 * frames_per_logical_second + \
                 ss * frames_per_logical_second + ff

    if drop_frame is False:
        return raw_frames, frac
    else:
        frames_dropped_per_inst = (frames_per_logical_second / 15)
        mins = hh * 60 + mm
        inst_count = mins - math.floor(mins / 10)
        dropped_frames = frames_dropped_per_inst * inst_count
        return raw_frames - dropped_frames, frac


def frame_count_to_smpte(frame_count: int, frames_per_logical_second: int, drop_frame: bool = False,
                         fractional_frame: float = None):
    assert frames_per_logical_second in [24,25,30,48,50,60]
    nominal_frames = frame_count
    separator = ":"
    if drop_frame:
        assert frames_per_logical_second in [30, 60]
        mins , _= divmod(nominal_frames, frames_per_logical_second * 60)
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
        return "%02i:%02i:%02i%s%02i%s" % (hh, mm, ss, separator, ff, ("%.3f" % fractional_frame)[1:])
    else:
        return "%02i:%02i:%02i%s%02i" % (hh, mm, ss, separator, ff)




