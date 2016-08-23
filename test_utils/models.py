from taskdj.models import BaseTask, BaseTag, BaseAnnotation, BaseTaskdUser
from django.db import models

class TestTag(BaseTag):
    pass

class TestAnnotation(BaseAnnotation):
    task = models.ForeignKey("TestTask", on_delete=models.CASCADE)

class TestTask(BaseTask):
    tags = models.ManyToManyField("TestTag", blank=True)

    @property
    def annotations(self):
        annotations = TestAnnotation.objects.filter(task=self)
        return annotations

class TestTaskNoRelations(BaseTask):
    pass

class TestTaskdUser(BaseTaskdUser):
    pass
