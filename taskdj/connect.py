import requests
import taskc

class TaskwarriorConnection(object):

    def __init__(self, taskd_user):
        self.user = taskd_user

    def connect(self):
        """
        Builds a connection to taskd. Assumes a .taskrc file is present with configuration data.
        """
        connection = taskc.simple.TaskdConnection.from_taskrc()
        connection.username = self.user.username
        connection.group = self.user.group

        if self.user.uuid == None:
            self.user.uuid = self._create_redshirt_user(connection.group)
            self.user.save()

        connection.uuid = self.user.uuid
        return connection

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

    def import_tasks(self):
        pass

    def export_task(self):
        pass
