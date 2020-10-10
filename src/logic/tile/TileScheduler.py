import json
import logging
from datetime import datetime
from typing import Dict

from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.job import Job
from apscheduler.schedulers.gevent import GeventScheduler

from logic import Constants
from logic.tile.Tile import Tile

LOGGER = logging.getLogger(Constants.APP_NAME)


class TileScheduler:
    def __init__(self, socketio):
        self.__socketio = socketio
        self.__jobs = {}
        self.__tiles = {}
        self.__cache = {}
        self.__scheduler = GeventScheduler()

    @staticmethod
    def get_full_name(pageName: str, tileName: str) -> str:
        return f'{pageName}_{tileName}'

    def register_tile(self, pageName: str, tile: Tile):
        fullName = self.get_full_name(pageName, tile.get_uniqueName())
        if fullName in self.__jobs:
            LOGGER.warning(f'Tile "{fullName}" already registered')

        job = self.__scheduler.add_job(tile.update, 'interval',
                                       [pageName],
                                       seconds=tile.get_intervalInSeconds(),
                                       next_run_time=datetime.now())

        self.__jobs[fullName] = job
        self.__cache[fullName] = None
        self.__tiles[fullName] = tile
        LOGGER.debug(f'Registered "{fullName}" (scheduled every {tile.get_intervalInSeconds()} seconds)')

    def unregister_tile(self, pageName: str, tile: Tile):
        fullName = self.get_full_name(pageName, tile.get_uniqueName())
        if fullName not in self.__jobs:
            LOGGER.warning(f'Tile "{fullName}" is not registered')

        self.__jobs[fullName].remove()
        del self.__jobs[fullName]
        del self.__cache[fullName]
        del self.__tiles[fullName]
        LOGGER.debug(f'Unregistered "{fullName}"')

    def emit_from_cache(self):
        for fullName, value in self.__cache.items():
            self.__emit_update(fullName, value)

    def run(self):
        def JobListener(event):
            if event.exception:
                LOGGER.error(event.exception)
            else:
                name, value = event.retval
                self.__cache[name] = value
                self.__emit_update(name, value)

        self.__scheduler.add_listener(JobListener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        self.__scheduler.start()

    def __emit_update(self, fullName: str, content: str):
        data = {'fullName': fullName, 'content': content}
        self.__socketio.emit('tileUpdate', json.dumps(data), namespace='/update')

    def get_tiles(self) -> Dict[str, Tile]:
        return self.__tiles

    def get_jobs(self) -> Dict[str, Job]:
        return self.__jobs

    def force_refresh(self, fullName: str):
        job = self.__get_job_by_name(fullName)
        if job is not None:
            LOGGER.debug(f'Manual refresh for tile "{fullName}"')
            job.modify(next_run_time=datetime.now())

    def __get_job_by_name(self, fullName: str) -> Job or None:
        if fullName not in self.__jobs:
            LOGGER.warning(f'Ignoring request to refresh non-existing tile "{fullName}"')
            return None
        return self.__jobs[fullName]
