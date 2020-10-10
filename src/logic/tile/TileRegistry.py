import logging

from logic import Constants
from logic.Registry import Registry
from logic.tile.Tile import Tile

LOGGER = logging.getLogger(Constants.APP_NAME)


class TileRegistry(Registry):
    """
    Scans for available tile implementations and provides access to them via class name
    """

    def __init__(self, package: str):
        super().__init__(package, Tile)
