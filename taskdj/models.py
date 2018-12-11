import datetime
import json
import uuid
import logging

from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator

logger = logging.getLogger(__name__)

class BaseTaskdUser(models.Model):
    """
    Abstract base class representing a user for interacting with taskd.
    """
    uuid = models.UUIDField(primary_key=False, unique=True)
    username = models.CharField(max_length=140, blank=True, null=True)
    certificate = models.TextField(blank=True)
    key = models.TextField(blank=True)
    group = models.CharField(max_length=120, default="Public")

    class Meta:
        abstract = True


class BaseTask(models.Model):
    """
    Abstract base class representing a single Taskwarrior task.

    In order for importing and exporting with annotations in tags to function, subclasses must supply a property for
    annotations and a ManyToManyField for tags. Also requires a ForeignKey relationship to the task from the
    annotation model. See test_utils/models.py for an example.
    """
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

    status = models.CharField(max_length=9, blank=False, choices=statuses, default="pending")
    uuid = models.UUIDField(blank=False, unique=True, default=uuid.uuid4)
    entry = models.DateTimeField(auto_now_add=True, editable=False)
    description = models.TextField(blank=False)
    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)
    due = models.DateTimeField(blank=True, null=True)
    until = models.DateTimeField(blank=True, null=True)
    scheduled = models.DateTimeField(blank=True, null=True)
    wait = models.DateTimeField(blank=True, null=True)
    recur = models.CharField(max_length=20, blank=True)
    parent = models.UUIDField(blank=True, null=True)
    # annotations = when making json, get all annotations related to self & add to json['annotations']
    # e.g., json['annotations'] = Annotations.objects.filter(task=self)
    project = models.CharField(max_length=50, blank=True)
    # tags = models.ManyToManyField("Tag", related_name="%(app_label)s_%(class)s_related", blank=True)
    priority = models.CharField(max_length=1, blank=True, choices=priorities, default="")
    # TODO: set as a one-to-many with other tasks
    depends = models.CharField(max_length=200, blank=True)

    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def export_to_json(self):
        """
        Exports model data to JSON in Taskwarrior format.
        """

        taskd_json = dict()
        time_format = "%Y%m%dT%H%M%SZ"
        taskd_json['status'] = self.status
        taskd_json['uuid'] = str(self.uuid) #prep for serialization
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
        taskd_json['modified'] = self.modified.strftime(time_format)

        if hasattr(self, "tags"):
            taskd_json['tags'] = [tag.name for tag in self.tags.all()]

        taskd_json['priority'] = self.priority
        return taskd_json

    @classmethod
    def import_tasks_from_taskd(cls, connection):
        """
        Pulls tasks from the taskserver for a given user and creates model objects for each one.
        Requires an instance of connect.TaskwarriorConnection.

        Usage:
            YourTaskModelClass.import_tasks_from_taskd()

        If relationships between your subclasses of BaseTask, BaseAnnotation and BaseTag exist, it will also create
        model objects with relationships for each tag and annotation.
        """
        tasks = connection.pull_tasks()
        for task in tasks:
            if hasattr(cls, "createdby") and hasattr(cls, "inlist"):
                # Advanced pizzacat nonsense
                # so object.create calls save() and we can't have blank tasks.
                task_model, created = cls.objects.get_or_create(uuid=task['uuid'], defaults={'createdby': connection.user.owner, 'inlist': connection.user.inbox, 'description': task['description']})
            elif hasattr(cls, "createdby"):
                # Basic user tracking
                task_model, created = cls.objects.get_or_create(createdby=connection.user.owner)

            else:
                # Vanilla model
                task_model = cls.objects.create()
            logger.debug("Task type: %s", type(task))
            if "tags" in task.keys() and hasattr(task_model, "tags"):  # drops tags if not represented in the model
                for tag_name in task['tags']:
                    # get or create tag model
                    if hasattr(cls, "createdby"):
                        tag_model = task_model.tags.get_or_create(name=tag_name, owner=connection.user.owner)[0]
                    else:
                        tag_model = task_model.tags.get_or_create(name=tag_name)[0]
                    tag_model.save()
                    # establish relationship between tag & current task
                    task_model.tags.add(tag_model)
            if "annotations" in task.keys() and hasattr(task_model, "annotations"):
                # create annotation model with a foreignkey to current task
                for annotation in task['annotations']:
                    annotation_model = task_model.annotations.create(task=task_model,
                                                                entry=annotation['entry'],
                                                                description=annotation['description'])
                    annotation_model.save()

            static_fields = [key for key in task.keys() if key not in ("tags", "annotations")]
            for key in static_fields:
                if key in ("entry", "end", "due", "scheduled", "wait"):
                    date = datetime.datetime.strptime(task[key], "%Y%m%dT%H%M%SZ")
                    logger.debug("date: %s, raw-value: %s ", date, task[key])
                    setattr(task_model, key, date)
                elif hasattr(task_model, key):
                    setattr(task_model, key, task[key])

            task_model.save()


class BaseAnnotation(models.Model):
    """
    Abstract base class representing a Taskwarrior annotation.

    In order for importing and exporting functions to work, subclasses must supply a ForeignKey relationship
    with the task model.
    """
    entry = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    class Meta:
        abstract = True


class BaseTag(models.Model):
    """
    Abstract base class representing a Taskwarrior tag.
    """
    name = models.CharField(max_length=140)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name
