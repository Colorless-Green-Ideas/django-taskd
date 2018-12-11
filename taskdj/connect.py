import json
import logging

import requests
from django.conf import settings

import taskc.simple
from taskdj.exceptions import TaskdConfigError, TaskdConnectionError

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


logger = logging.getLogger(__name__)


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
            TW_CLIENT_CERT: The application's client certificate.
            TW_CLIENT_KEY:  The application's client key.
            TW_SERVER:      The taskserver's address.
            TW_CA_CERT:     The taskserver's CA certificate.
        Optional settings:
            TW_PORT:        If none is supplied, uses default: 53589
        """
        if taskrc:
            self._connection = taskc.simple.TaskdConnection.from_taskrc(taskrc=taskrc)
        elif hasattr(settings, 'TASKRC'):
            self._connection = taskc.simple.TaskdConnection.from_taskrc(taskrc=settings.TASKRC)
        else:
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
            self._connection.cacert_file = settings.TW_CA_CERT
            if self.user.username:
                # check if username is overriden? idk how this works - jack
                self._connection.username = self.user.username
            else:
                # Get the django username then
                self._connection.username = self.user.owner.username

        if hasattr(self.user, "group"):
            self._connection.group = self.user.group
        elif hasattr(settings, 'TW_DEFAULT_GROUP'):
            self._connection.group = settings.TW_DEFAULT_GROUP
        else:
            raise TaskdConfigError("No group found. Is TW_DEFAULT_GROUP in settings.py?")

        if not self.user.uuid:
            self.user.uuid = self._create_redshirt_user(self._connection.group)
            cert, key = self._create_redshirt_certs()
            self.user.certificate = cert
            self.user.key = key
            self.user.save()
        else:
            logger.info("Not generating certs.")

        self._connection.uuid = self.user.uuid

    def pull_tasks(self):
        """
        Pulls all tasks from the taskserver and returns them as a list of dicts.
        """
        self._check_connection()

        response = self._connection.pull()
        response.raise_for_status()
        self.user.sync_key = response.sync_key
        tasks = [json.loads(task) for task in response.data]
        self.user.save()
        return tasks

    def push_tasklist(self, tasklist):
        """
        Pushes a tasklist to the taskserver.
        """
        self._check_connection()
        if self.user.sync_key:
            mangled_tasks = self.user.sync_key + '\n' + '\n'.join(tasklist)
        else:
            # Should only run the first time.
            mangled_tasks = '\n'.join(tasklist)
        logger.info("Final tasks:\n %s", mangled_tasks)
        response = self._connection.put(mangled_tasks)

        response.raise_for_status()
        self.user.sync_key = response.sync_key
        self.user.save()


    def _create_redshirt_user(self, group):
        """
        Creates a user on redshirt, and returns the server-generated uuid to store in the TaskdUser model.
        """
        url = urlparse.urlunparse(("http", "redshirt:4000", "/add_user/{0}/{1}".format(group, self._connection.username), '', '', ''))
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    def _create_redshirt_certs(self):
        """
        Contact redshirt to generate keypair with taskd's built in pki kit.

        Returns the certificate and the key.
        """
        response = requests.get("http://redshirt:4000/create_cert/{0}".format(self._connection.username))
        response.raise_for_status()
        keypair = response.json()
        return keypair['certificate'], keypair['key']

    def _check_connection(self):
        """
        Checks for a TaskdConnection object, and if none is present calls connect().
        """
        if self._connection is None:
            try:
                self.connect()
            except IOError as e:
                raise TaskdConnectionError(e, "Could not automatically connect to taskd.")
            except TaskdConfigError as e:
                raise e
