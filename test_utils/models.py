from taskdj.models import BaseTask, BaseTag, BaseAnnotation
from django.db import models

class TestTag(BaseTag):
    pass

class TestAnnotation(BaseAnnotation):
    task = models.ForeignKey("TestTask", on_delete=models.CASCADE)

class TestTask(BaseTask):
    tags = models.ManyToManyField("TestTag", blank=True)

    def __init__(self):
        super(TestTask, self).__init__()

    @property
    def annotations(self):
        annotations = TestAnnotation.objects.filter(task=self)
        return annotations
