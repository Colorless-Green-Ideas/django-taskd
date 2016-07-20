from django.conf import settings
from django.test import TestCase

try:
    import unittest.mock as mock
except ImportError:
    import mock

from random import randint

from test_utils.models import TestTask, TestAnnotation, TestTag, TestTaskNoRelations

ANNOTATION_COUNT = 5
TAG_COUNT = 5

class BaseTaskTest(TestCase):
    def setUp(self):
        self.task = TestTask.objects.create()

        self.annotations = []
        for i in range(ANNOTATION_COUNT):
            desc = "This is annotation number {0}".format(i)
            annotation = TestAnnotation.objects.create(task=self.task, description=desc)
            self.annotations.append(annotation)

        self.tags = []
        self.all_tags = []
        for i in range(TAG_COUNT):
            name = "This is tag number {0}".format(i)
            tag = TestTag.objects.create(name=name)
            self.all_tags.append(tag)
            n = randint(0, 1)
            if n == 1:
                self.task.tags.add(tag)
                self.tags.append(tag)

    def test_task_gets_correct_annotations(self):
        for annotation in self.annotations:
            self.assertTrue(annotation in self.task.annotations)

    def test_task_gets_correct_tags(self):
        for tag in self.tags:
            self.assertTrue(tag in self.task.tags.all())

    def test_annotations_in_json(self):
        json = self.task.export_to_json()
        for annotation in self.task.annotations:
            test_dict = {'entry': annotation.entry, 'description': annotation.description}
            self.assertTrue(test_dict in json['annotations'])

    def test_tags_in_json(self):
        json = self.task.export_to_json()
        for tag in self.all_tags:
            if tag in self.tags:
                self.assertTrue(tag.name in json['tags'])
            else:
                self.assertTrue(tag.name not in json['tags'])

    def test_without_tags_or_annotations_in_json(self):
        task = TestTaskNoRelations.objects.create()
        json = task.export_to_json()
        self.assertTrue('annotations' not in json.keys())
        self.assertTrue('tags' not in json.keys())

@mock.patch('taskdj.connect.TaskwarriorConnection', autospec=True)
class TaskDynamicRelationshipTest(TestCase):

    def setUp(self):
        # we need to generate test task data for this; possibly a test_utils function?
        self.tasklist = None
        self.tasklist_norel = None

    def test_import_with_no_relationships(self, mock_connection):
        mock_connection.return_value.get_tasks.return_value = self.tasklist_norel
        TestTaskNoRelations.import_tasks_from_taskd(mock_connection)
        task_qs = TestTaskNoRelations.objects.all()
        for task in self.tasklist:
            self.assertTrue(task_qs.filter(uuid__exact=task['uuid']).exists())

    def test_import_from_taskd_instantiates_dynamic_relationships(self, mock_connection):
        mock_connection.return_value.get_tasks.return_value = self.tasklist
        TestTask.import_tasks_from_taskd(mock_connection)
        tag_qs = TestTag.objects.all()
        annotation_qs = TestAnnotation.objects.all()
        for task in self.tasklist:
            if hasattr(task, "tags"):
                for tag in task['tags']:
                    self.assertTrue(tag_qs.filter(name__exact=tag['name']).exists())
            if hasattr(task, "annotations"):
                for annotation in task['annotations']:
                    self.assertTrue(annotation_qs.filter(entry__exact=annotation['entry']).exists())
                    self.assertTrue(annotation_qs.filter(description__exact=annotation['description']).exists())
