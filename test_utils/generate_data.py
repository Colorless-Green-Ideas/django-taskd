import datetime
import json
import random
import uuid
import os

DEFAULT_TEST_LISTS_MIN = 3
DEFAULT_TEST_LISTS_MAX = 50
DEFAULT_TEST_ANNOTATIONS = 5
DEFAULT_TEST_TAGS = 5


class TestData(object):

    def __init__(self):
        self.text = SampleText()

    def tasklist(self, relationships=True, tasks=random.randint(DEFAULT_TEST_LISTS_MIN, DEFAULT_TEST_LISTS_MAX)):
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
            taskd_json['description'] = self.text.sentence()
            if relationships:
                taskd_json['annotations'] = self.annotations()
                taskd_json['tags'] = self.tags()
            taskd_json['project'] = "testing"
            taskd_json['priority'] = priorities[random.randint(0, 3)]

            # taskd_json = json.dumps(taskd_json) 
            tasklist.append(taskd_json)
        return tasklist

    def annotations(self, annotations=random.randint(1,DEFAULT_TEST_ANNOTATIONS)):
        annotation_list = []
        for annotation in range(0, annotations):
            annotation_json = dict()
            time_format = "%Y%m%dT%H%M%SZ"
            annotation_json['entry'] = datetime.datetime.now().strftime(time_format)
            annotation_json['description'] = self.text.sentence()
            annotation_list.append(annotation_json)
        return annotation_list

    def tags(self, tags=random.randint(1, DEFAULT_TEST_TAGS)):
        tag_list = []
        for tag in range(0, tags):
            word = self.text.word()
            tag_list.append(word)
        return tag_list

    def timestamp(self, before=datetime.datetime.now(), after=None):
        pass


class SampleText(object):

    def __init__(self, fn='lorem.txt'):
        with open(os.path.abspath(os.path.dirname(__file__)) + '/' + fn, 'r') as f:
            self.text = f.readlines()

    def sentence(self):
        index = random.randint(0, len(self.text) - 1)
        sentence = self.text[index]
        return sentence

    def word(self):
        line = self.sentence()
        words = line.split(' ')
        index = random.randint(0, len(words) - 1)
        word = words[index]
        return word
