from fractions import Fraction
import re
from typing import Optional

def footage_to_seconds(footage: str) -> Optional[Fraction]:
    m = re.match(r'(\d+)\+(\d+)(\.\d+)?', footage)
    if m is None:
        return None

    feet, frames, _ = m.groups()
    feet, frames = int(feet), int(frames)

    fps = 24
    frames_per_foot = 16

    total_frames = feet * frames_per_foot + frames

    return Fraction(total_frames, fps)
