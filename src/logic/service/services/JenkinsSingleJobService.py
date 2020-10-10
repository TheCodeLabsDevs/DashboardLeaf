from typing import Dict

import jenkins
from TheCodeLabs_BaseUtils import CachedService


class JenkinsSingleJobService(CachedService):
    def __init__(self, settings):
        super().__init__(settings['fetchIntervalInSeconds'])
        self._settings = settings
        self._jenkins = jenkins.Jenkins(url=self._settings['hostname'],
                                        username=self._settings['user'],
                                        password=self._settings['password'])

    def _fetch_data(self) -> Dict:
        return self._jenkins.get_job_info(name=self._settings['jobName'])
