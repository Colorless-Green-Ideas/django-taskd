from django.test import TestCase

from taskdj.models import Annotation, BaseTaskdUser, BaseTaskdTask

class BaseTaskdTaskTest(TestCase):
    def setUp(self):
        self.task = BaseTaskdTask.objects.create()
        self.annotation_1 = Annotation.objects.create(task=self.task, description="This is the first annotation.")
        self.annotation_2 = Annotation.objects.create(task=self.task, description="This is the second annotation.")

    def test_task_gets_correct_annotations(self):
        self.assertEqual(self.task.annotations, [self.annotation_1, self.annotation_2])

