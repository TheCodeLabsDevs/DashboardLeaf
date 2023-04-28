from dataclasses import dataclass
from typing import Dict


@dataclass
class TileLayoutSettings:
    x: int
    y: int
    width: int
    height: int


@dataclass
class PageInstance:
    uniqueName: str
    tileLayouts: Dict[str, TileLayoutSettings]

    def get_tile_layouts_sorted(self):
        return {k: v for k, v in sorted(self.tileLayouts.items(), key=lambda item: item)}
