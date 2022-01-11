from fractions import Fraction
import re
import math
from collections import namedtuple
from typing import Optional

def footage_to_seconds(footage: str) -> Optional[Fraction]:
    m = re.match(r'(\d+)\+(\d+)(\.\d+)?')
    if m is None:
        return None

    feet, frames = m.groups()
    feet, frames = int(feet), int(frames)

    fps = 24
    frames_per_foot = 16

    total_frames = feet * 16 + frames

    return Fraction(total_frames, fps)