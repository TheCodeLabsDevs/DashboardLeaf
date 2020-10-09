from dataclasses import dataclass
from typing import Dict


@dataclass
class TileLayoutSettings:
    x: int
    y: int
    width: int
    height: int


@dataclass()
class PageInstance:
    uniqueName: str
    tileLayouts: Dict[str, TileLayoutSettings]
