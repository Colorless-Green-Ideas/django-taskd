import uuid
from django.db import models

class BaseTaskdUser(models.Model):
    uuid = models.UUIDField(primary_key=False, unique=True)
    username = models.CharField(max_length=140)
    certificate = models.TextField(blank=True, null=True)
    key = models.TextField(blank=True, null=True)
    group = models.CharField(max_length=120, default="Public")

    class Meta:
        abstract = True
        app_label = "taskdj"

class BaseTaskdTask(models.Model):
    statuses = (
            ("pending", "Pending"),
            ("deleted", "Deleted"),
            ("completed", "Completed"),
            ("waiting", "Waiting"),
            ("recurring", "Recurring")
        )
    priorities = (
            ("H", "High"),
            ("M", "Medium"),
            ("L", "Low")
        )

    status = models.CharField(max_length=9, blank=False, null=False, choices=statuses, default="pending")
    uuid = models.UUIDField(blank=False, unique=True, editable=False, default=uuid.uuid4)
    entry = models.DateTimeField(auto_add_now=True)
    description = models.TextField(blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True))
    due = models.DateTimeField(blank=True, null=True)
    until = models.DateTimeField(blank=True, null=True)
    scheduled = models.DateTimeField(blank=True, null=True)
    wait = models.DateTimeField(blank=True, null=True)
    recur = models.CharField(max_length=20, blank=True, null=True)
    parent = models.UUIDField(blank=True, null=True)
    # annotations = when making json, get all annotations related to self & add to json['annotations']
    # e.g., json['annotations'] = Annotations.objects.filter(task=self)
    project = models.CharField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    priority = models.CharField(max_length=1, blank=True, null=True, choices=priorities, default=None)
    # TODO: set as a one-to-many with other tasks
    depends = models.CharField(blank=True, null=True)

    class Meta:
        abstract = True
        app_label = "taskdj"

    def annotations(self):
        annotations = Annotation.objects.filter(task=self)
        return annotations

    def get_taskd_json(self):
 	"""
 	Builds a JSON in Taskwarrior format that contains the task's information.
 	"""
 	taskd_json = dict()
 	time_format = "%Y%m%dT%H%M%SZ"
 	taskd_json['status'] = status
 	taskd_json['uuid'] = uuid
 	taskd_json['entry'] = start.strftime(time_format)
 	if end:
 		taskd_json['end'] = end.strftime(time_format)
 	taskd_json['description'] = description
 	taskd_json['annotations'] = self.annotations()
 	taskd_json['project'] = project
 	taskd_json['tags'] = [tag.name for tag in tags.all()]
 	taskd_json['priority'] = priority
 	return taskd_json        

class Annotation(models.Model):
    task = models.ForeignKey(BaseTask, on_delete=models.CASCADE)
    entry = models.DateTimeField(auto_add_now=True)
    description = model.TextField(blank=True)

class Tag(models.Model):
    name = models.CharField(max_length=140)

    def __unicode__(self):
        return self.name
