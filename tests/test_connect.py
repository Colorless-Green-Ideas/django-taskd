import uuid

try:
    import unittest.mock as mock
except ImportError:
    import mock

from django.test import TestCase, override_settings

from taskdj.connect import TaskwarriorConnection
from taskdj.exceptions import TaskdConnectionError, TaskdConfigError
from test_utils.models import TestTaskdUser
from test_utils.generate_data import TestData


class UnitTestConnect(TestCase):

    def setUp(self):
        self.user = TestTaskdUser(username="test_user")
        self.connection = TaskwarriorConnection(self.user)
        self.data = TestData()

    def test_connection_is_None_on_instantiation(self):
        self.assertEqual(self.connection._connection, None)

    def test_connect_without_taskrc_or_settings_raises_error(self):
        with self.assertRaises(TaskdConfigError):
            self.connection.connect()

    @override_settings(TW_CLIENT_CERT='test_cert', TW_CLIENT_KEY='test_key', TW_SERVER='test_server')
    def test_connect_without_taskrc_and_missing_settings_raises_error(self):
        with self.assertRaises(TaskdConfigError):
            self.connection.connect()

    @mock.patch('taskdj.connect.TaskwarriorConnection._create_redshirt_user')
    @override_settings(TW_CLIENT_CERT='test_cert', TW_CLIENT_KEY='test_key', TW_SERVER='test_server',
                       TW_PORT='test_port', TW_CA_CERT='test_ca_cert')
    def test_connect_without_taskrc_and_all_settings_sets_attributes(self, mock_create_redshirt_user):
        test_uuid = uuid.uuid4()
        mock_create_redshirt_user.return_value = test_uuid
        self.assertEqual(self.user.uuid, None)
        self.connection.connect()
        self.assertEqual(self.connection._connection.client_cert, "test_cert")
        self.assertEqual(self.connection._connection.client_key, "test_key")
        self.assertEqual(self.connection._connection.server, "test_server")
        self.assertEqual(self.connection._connection.port, "test_port")
        self.assertEqual(self.connection._connection.cacert, "test_ca_cert")
        self.assertEqual(self.connection._connection.username, self.user.username)
        self.assertEqual(self.connection._connection.group, self.user.group)
        self.assertEqual(self.connection._connection.uuid, test_uuid)
        self.assertEqual(self.user.uuid, test_uuid)

    @mock.patch('taskc.simple.TaskdConnection')
    def test_pull_tasks_returns_list_of_task_dicts(self, mock_taskd_connection):
        tasklist = self.data.tasklist()
        test_response = mock.Mock()
        test_response.sync_key = "test_sync_key"
        test_response.data = tasklist
        mock_taskd_connection.return_value.pull.return_value = test_response
        self.connection._connection = mock_taskd_connection
        for task in self.connection.pull_tasks():
            self.assertIn(task, tasklist)
            self.assertIsInstance(task, dict)
