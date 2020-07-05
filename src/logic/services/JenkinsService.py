import jenkins


class JenkinsService:

    def __init__(self, server, username, password, view_name):
        self.__jenkins = jenkins.Jenkins(url=server, username=username, password=password)
        self.__view_name = view_name

    def get_jobs(self):
        return self.__jenkins.get_jobs(view_name=self.__view_name)
