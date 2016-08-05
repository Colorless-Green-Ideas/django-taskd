import requests
import taskc
import json

from taskdj.exceptions import TaskdConnectionError

class TaskwarriorConnection(object):

    def __init__(self, taskd_user):
        self.user = taskd_user
        self._connection = None

    def connect(self):
        """
        Builds a connection to taskd. Assumes a .taskrc file is present with configuration data.
        """
        self._connection = taskc.simple.TaskdConnection.from_taskrc()
        self._connection.username = self.user.username
        self._connection.group = self.user.group

        if self.user.uuid is None:
            self.user.uuid = self._create_redshirt_user(connection.group)
            self.user.save()

        self._connection.uuid = self.user.uuid

    def _create_redshirt_user(self, group):
        """
        Creates a user on redshirt, and returns the server-generated uuid to store in the TaskdUser model.
        """
        url = urlparse.urlunparse(("http", "redshirt:4000", "/add_user/{0}/{1}".format(group, self.user.name), '', '', ''))
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    def _create_redshirt_certs(self):
        """
        Contact redshirt to generate keypair with taskd's built in pki kit.

        Returns the certificate and the key.
        """
        response = requests.get("http://redshirt:4000/create_cert/{0}".format(self.user.username))
        response.raise_for_status()
        keypair = response.json()
        return keypair['certificate'], keypair['key']

    def get_tasks(self):
        if self._connection is None:
            try:
                self._connection = self.connect()
            except IOError as e:
                raise TaskdConnectionError("Could not automatically connect to taskd.") from e

        response = self._connection.pull()
        self.user.sync_key = response.sync_key
        response.raise_for_status()
        tasks = [json.loads(task) for tasks in response.data]
        return tasks

    def export_task(self, task):
        pass
