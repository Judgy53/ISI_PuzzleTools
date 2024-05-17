from dataclasses import dataclass, field
import time
from shiftingBlock.Grid import Grid

@dataclass(order=True)
class PrioritizedGrid:
    priority: int
    creation_time: float
    grid: Grid=field(compare=False)