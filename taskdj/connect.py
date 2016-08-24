import requests
import taskc.simple
import json
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from taskdj.exceptions import TaskdConnectionError, TaskdConfigError

class TaskwarriorConnection(object):

    def __init__(self, taskd_user):
        self.user = taskd_user
        self._connection = None

    def connect(self, taskrc=None):
        """
        Builds a connection to taskd. If taskrc is specified, uses settings from the .taskrc file otherwise attempts
        to build manually using django settings.
        Raises TaskdConfigError if settings are not found when taskrc is empty.

        Required settings:
            TW_CLIENT_CERT: the application's client certificate.
            TW_CLIENT_KEY:  the application's client key.
            TW_SERVER:      the taskserver's address.
            TW_CA_CERT:     the taskserver's CA certificate.

        """
        if taskrc:
            self._connection = taskc.simple.TaskdConnection.from_taskrc(taskrc=taskrc)
        else:
            from django.conf import settings
            try:
                assert settings.TW_CLIENT_CERT
                assert settings.TW_CLIENT_KEY
                assert settings.TW_SERVER
                assert settings.TW_CA_CERT
            except (AssertionError, AttributeError) as e:
                raise TaskdConfigError(e)
            self._connection = taskc.simple.TaskdConnection()
            self._connection.client_cert = settings.TW_CLIENT_CERT
            self._connection.client_key = settings.TW_CLIENT_KEY
            self._connection.server = settings.TW_SERVER
            self._connection.port = settings.TW_PORT
            self._connection.cacert = settings.TW_CA_CERT
        self._connection.username = self.user.username
        self._connection.group = self.user.group

        if self.user.uuid is None:
            self.user.uuid = self._create_redshirt_user(self._connection.group)
            self.user.save()

        self._connection.uuid = self.user.uuid

    def _create_redshirt_user(self, group):
        """
        Creates a user on redshirt, and returns the server-generated uuid to store in the TaskdUser model.
        """
        url = urlparse.urlunparse(("http", "redshirt:4000", "/add_user/{0}/{1}".format(group, self.user.username), '', '', ''))
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
                raise TaskdConnectionError(e, "Could not automatically connect to taskd.")

        response = self._connection.pull()
        self.user.sync_key = response.sync_key
        response.raise_for_status()
        tasks = [json.loads(task) for tasks in response.data]
        return tasks

    def export_task(self, task):
        pass
