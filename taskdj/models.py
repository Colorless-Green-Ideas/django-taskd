import uuid
from django.db import models

class BaseUser(models.Model):
    uuid = models.UUIDField(primary_key=False, unique=True)
    username = models.CharField(max_length=140)
    certificate = models.TextField(blank=True, null=True)
    key = models.TextField(blank=True, null=True)
    group = models.CharField(max_length=120, default="Public")

    class Meta:
        abstract = True
        app_label = "taskdj"

class BaseTask(models.Model):
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
    entry = models.DateTimeField(auto_now_add=True, editable=False)
    description = models.TextField(blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    due = models.DateTimeField(blank=True, null=True)
    until = models.DateTimeField(blank=True, null=True)
    scheduled = models.DateTimeField(blank=True, null=True)
    wait = models.DateTimeField(blank=True, null=True)
    recur = models.CharField(max_length=20, blank=True, null=True)
    parent = models.UUIDField(blank=True, null=True)
    # annotations = when making json, get all annotations related to self & add to json['annotations']
    # e.g., json['annotations'] = Annotations.objects.filter(task=self)
    project = models.CharField(max_length=50, blank=True, null=True)
    # tags = models.ManyToManyField("Tag", related_name="%(app_label)s_%(class)s_related", blank=True)
    priority = models.CharField(max_length=1, blank=True, null=True, choices=priorities, default=None)
    # TODO: set as a one-to-many with other tasks
    depends = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        abstract = True
        app_label = "taskdj"

    """
    @property
    def annotations(self):
        annotations = BaseAnnotation.objects.filter(task=self)
        return annotations
    """

    def export_to_json(self):
        """
        Exports model data to JSON in Taskwarrior format.
        """
        taskd_json = dict()
        time_format = "%Y%m%dT%H%M%SZ"
        taskd_json['status'] = self.status
        taskd_json['uuid'] = self.uuid
        taskd_json['entry'] = self.entry.strftime(time_format)
        if self.end:
 	        taskd_json['end'] = self.end.strftime(time_format)
        taskd_json['description'] = self.description

        if hasattr(self, "annotations"):
            taskd_json['annotations'] = []
            for annotation in self.annotations:
                annotation_dict = dict()
                annotation_dict['entry'] = annotation.entry
                annotation_dict['description'] = annotation.description
                taskd_json['annotations'].append(annotation_dict)

        taskd_json['project'] = self.project

        if hasattr(self, "tags"):
            taskd_json['tags'] = [tag.name for tag in self.tags.all()]

        taskd_json['priority'] = self.priority
        return taskd_json 

class BaseAnnotation(models.Model):
    entry = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    
    class Meta:
        abstract = True
        app_label = "taskdj"

class BaseTag(models.Model):
    name = models.CharField(max_length=140)

    class Meta:
        abstract = True
        app_label = "taskdj"

    def __unicode__(self):
        return self.name
