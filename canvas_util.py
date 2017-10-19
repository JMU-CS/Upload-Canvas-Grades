"""
Utilities for submitting grades and comments throught the Canvas API.

Documentation here:

https://canvas.beta.instructure.com/doc/api/submissions.html#method.submissions_api.update

"""
import sys
import urllib
import time
import urllib2

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
            comment_key = 'grade_data[{}][text_comment]'.format(student_id)
            form_data[comment_key] = comment

        data = urllib.urlencode(form_data)
        header = {"Authorization" : "Bearer {}".format(self.key)}
        request = urllib2.Request(self.url, data, headers=header)
        attempt_count = 0
        while attempt_count < 4:
            try:
                return urllib2.urlopen(request)
            except urllib2.URLError as e:
                print "URL ERROR, trying again " + str(e)
                time.sleep(.5)
                attempt_count += 1
        print "Giving up."


if __name__ == "__main__":
    COURSE_ID = "1464214"
    ASSIGNMENT_ID = "8297096"
    student_id = "5449287"
    gp = GradePoster(COURSE_ID, ASSIGNMENT_ID, sys.argv[1])
    response = gp.post_grade_update(student_id, "101.5", "Awesome Job!")
    print response.read()
