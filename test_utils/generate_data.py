import datetime
import json
import random
import uuid
import os

DEFAULT_TEST_LISTS_MIN = 3
DEFAULT_TEST_LISTS_MAX = 50
DEFAULT_TEST_ANNOTATIONS = 5
DEFAULT_TEST_TAGS = 5

with open(os.path.abspath(os.path.dirname(__file__)) + '/lorem.txt', 'r') as f:
    LOREM_LINES = f.readlines()

def generate_taskd_json(relationships=True, tasks=random.randint(DEFAULT_TEST_LISTS_MIN, DEFAULT_TEST_LISTS_MAX)):
    tasklist = []
    statuses = ["pending", "deleted", "completed", "waiting", "recurring"]
    priorities = ["L", "M", "H", ""]
    time_format = "%Y%m%dT%H%M%SZ"
    for task in range(0, tasks):
        taskd_json = dict()
        taskd_json['status'] = statuses[random.randint(0, 4)]
        taskd_json['uuid'] = str(uuid.uuid4())
        taskd_json['entry'] = datetime.datetime.now().strftime(time_format)
        taskd_json['end'] = datetime.datetime.now().strftime(time_format)
        taskd_json['description'] = _get_random_desc()
        if relationships:
            taskd_json['annotations'] = _make_annotations()
            taskd_json['tags'] = _make_tags()
        taskd_json['project'] = "testing"
        taskd_json['priority'] = priorities[random.randint(0, 3)]

        taskd_json = json.dumps(taskd_json)
        tasklist.append(taskd_json)
    return tasklist

def _get_random_desc():
    index = random.randint(0, len(LOREM_LINES) - 1)
    desc = LOREM_LINES[index]
    return desc

def _make_annotations(annotations=random.randint(1,DEFAULT_TEST_ANNOTATIONS)):
    annotation_list = []
    for annotation in range(0, annotations):
        annotation_json = dict()
        time_format = "%Y%m%dT%H%M%SZ"
        annotation_json['entry'] = datetime.datetime.now().strftime(time_format)
        annotation_json['description'] = _get_random_desc()
        annotation_list.append(annotation_json)
    return annotation_list

def _make_tags(tags=random.randint(1, DEFAULT_TEST_TAGS)):
    tag_list = []
    for tag in range(0, tags):
        line = LOREM_LINES[random.randint(0, len(LOREM_LINES) - 1)]
        words = line.split(' ')
        word = words[random.randint(0, len(words) - 1)]
        tag_list.append(word)
    return tag_list
