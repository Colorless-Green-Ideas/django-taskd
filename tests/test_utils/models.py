from taskdj.models import BaseTask, BaseTag, BaseAnnotation
from django.db import models

class TestTag(BaseTag):
    pass

class TestAnnotation(BaseAnnotation):
    task = models.ForeignKey("TestTask", on_delete=models.CASCADE)

class TestTask(BaseTask):
    def __init__(self):
        super(TestTask, self).__init__()

        tags = models.ManyToManyField(TestTag, null=True, blank=True)
        annotations = self.annotations()

    def annotations(self):
        annotations = TestAnnotation.objects.filter(task=self)
        return annotations
