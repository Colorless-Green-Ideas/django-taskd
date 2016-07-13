from django.conf import settings
from django.test import TestCase

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
