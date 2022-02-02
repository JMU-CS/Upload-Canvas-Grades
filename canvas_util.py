"""
Utilities for submitting grades and comments throught the Canvas API.

Documentation here:

https://canvas.beta.instructure.com/doc/api/submissions.html#method.submissions_api.update

"""
import sys
import urllib 
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError
import time
import json


import sys
import pathlib

# https://stackoverflow.com/a/61901696
def get_datadir() -> pathlib.Path:

    """
    Returns a parent directory path
    where persistent application data can be stored.

    # linux: ~/.local/share
    # macOS: ~/Library/Application Support
    # windows: C:/Users/<USER>/AppData/Roaming
    """

    home = pathlib.Path.home()

    if sys.platform == "win32":
        return home / "AppData/Roaming"
    elif sys.platform == "linux":
        return home / ".local/share"
    elif sys.platform == "darwin":
        return home / "Library/Application Support"

def get_config(config_name):
    """Return the Path object for the config file, creating an empty file
    if it doesn't already exist.

    """
    config_dir = get_datadir() / "jmu_canvas_uploader"
    try:
        config_dir.mkdir(parents=True)
    except FileExistsError:
        pass
    config_path = config_dir / config_name

    if not config_path.is_file():
        config_path.touch()

    return config_path


    
def get_course_info(course_id, key):
    url = f"https://canvas.jmu.edu/api/v1/courses/{course_id}"
    header = {"Authorization" : "Bearer {}".format(key)}
    request = urllib.request.Request(url, None, headers=header)
    return json.loads(urlopen(request).read())

def get_assignment_info(course_id, assignment_id, key):
    url = f"https://canvas.jmu.edu/api/v1/courses/{course_id}/assignments/{assignment_id}"
    header = {"Authorization" : "Bearer {}".format(key)}
    request = urllib.request.Request(url, None, headers=header)
    return json.loads(urlopen(request).read())

class GradePoster(object):

    def __init__(self, course_id, assignment_id, key):
        url_string = ("https://canvas.jmu.edu/api/v1/courses/{}"
                      "/assignments/{}/submissions/update_grades")
        self.url = url_string.format(course_id, assignment_id)
        self.key = key

    def post_grade_update(self, student_id, grade, comment=""):
        form_data = {}

        grade_key = 'grade_data[{}][posted_grade]'.format(student_id)
        form_data[grade_key] = grade

        if comment != "":
            #print('adding comment:', comment)
            comment_key = 'grade_data[{}][text_comment]'.format(student_id)
            form_data[comment_key] = comment

        data = urlencode(form_data).encode('utf-8')
        #print('self url is:', self.url)
        #print(data)
        header = {"Authorization" : "Bearer {}".format(self.key)}
        #print(header)
        request = urllib.request.Request(self.url, data, headers=header)
        #print('request is:')
        #print(request)
        #print ('-----')
        attempt_count = 0
        while attempt_count < 4:
            try:
                #return urllib2.urlopen(request)
                #return urllib.request.urlopen(request)
                return urlopen(request)
            except URLError as e:
                print( "URL ERROR, trying again " + str(e))
                time.sleep(.5)
                attempt_count += 1
        print("Giving up.")


"""
The code below is ONLY for testing the above API
and is not run during the normal posting events
If you want to test changes to this module, change
the course_id, assignment_id, and student_id (test student is
a good one to test with).
"""
if __name__ == "__main__":
    get_config("config.ini")
    
    print(get_assignment_info( '1848558','15003267', sys.argv[1])['name'])
