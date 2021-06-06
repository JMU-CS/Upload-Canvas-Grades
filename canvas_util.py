"""
Utilities for submitting grades and comments throught the Canvas API.

Documentation here:

https://canvas.beta.instructure.com/doc/api/submissions.html#method.submissions_api.update

"""
import sys
import urllib 
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import URLError
import time

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
    COURSE_ID = "1744815"
    ASSIGNMENT_ID = "12338724"
    student_id = "5745951"
    gp = GradePoster(COURSE_ID, ASSIGNMENT_ID, sys.argv[1])
    print('running this')
    response = gp.post_grade_update(student_id, "101.5", "Awesome Job!")
    print(response.read())
