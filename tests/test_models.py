from django.conf import settings
from django.test import TestCase

from test_utils.models import TestTask, TestAnnotation

class BaseTaskTest(TestCase):
    def setUp(self):
        self.task = TestTask.objects.create()
        self.annotation_1 = TestAnnotation.objects.create(task=self.task, description="This is the first annotation.")
        self.annotation_2 = TestAnnotation.objects.create(task=self.task, description="This is the second annotation.")

    def test_task_gets_correct_annotations(self):
        self.assertTrue(self.annotation_1 in self.task.annotations())
