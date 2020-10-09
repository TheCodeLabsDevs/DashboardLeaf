import json
import logging
from datetime import datetime
from typing import Dict

from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.job import Job
from apscheduler.schedulers.gevent import GeventScheduler

from logic import Constants
from tile.Tile import Tile

LOGGER = logging.getLogger(Constants.APP_NAME)


class TileScheduler:
    def __init__(self, socketio):
        self.__socketio = socketio
        self.__jobs = {}
        self.__tiles = {}
        self.__cache = {}
        self.__scheduler = GeventScheduler()

    def RegisterTile(self, tile: Tile):
        name = tile.get_uniqueName()
        if name in self.__jobs:
            LOGGER.warning(f'Tile "{name}" already registered')

        job = self.__scheduler.add_job(tile.update, 'interval',
                                       seconds=tile.get_intervalInSeconds(),
                                       next_run_time=datetime.now())

        self.__jobs[name] = job
        self.__cache[name] = None
        self.__tiles[name] = tile
        LOGGER.debug(f'Registered "{name}" (scheduled every {tile.get_intervalInSeconds()} seconds)')

    def UnregisterTile(self, tile: Tile):
        name = tile.get_uniqueName()
        if name not in self.__jobs:
            LOGGER.warning(f'Tile "{name}" is not registered')

        self.__jobs[name].remove()
        del self.__jobs[name]
        del self.__cache[name]
        del self.__tiles[name]
        LOGGER.debug(f'Unregistered "{name}"')

    def EmitFromCache(self):
        for name, value in self.__cache.items():
            self.__EmitUpdate(name, value)

    def Run(self):
        def JobListener(event):
            if event.exception:
                LOGGER.error(event.exception)
            else:
                name, value = event.retval
                self.__cache[name] = value
                self.__EmitUpdate(name, value)

        self.__scheduler.add_listener(JobListener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        self.__scheduler.start()

    def __EmitUpdate(self, uniqueName: str, content: str):
        data = {'uniqueName': uniqueName, 'content': content}
        self.__socketio.emit('tileUpdate', json.dumps(data), namespace='/update')

    def GetTiles(self) -> Dict[str, Tile]:
        return self.__tiles

    def GetJobs(self) -> Dict[str, Job]:
        return self.__jobs

    def ForceRefresh(self, tileName):
        job = self.__GetJobByName(tileName)
        if job is not None:
            LOGGER.debug(f'Manual refresh for tile "{tileName}"')
            job.modify(next_run_time=datetime.now())

    def __GetJobByName(self, tileName) -> Job or None:
        if tileName not in self.__jobs:
            LOGGER.warning(f'Ignoring request to refresh non-existing tile "{tileName}"')
            return None
        return self.__jobs[tileName]
