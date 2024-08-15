"""Script for bulk-updating the roster of a Canvas course. Students
are enrolled or removed to match the provided roster.

Author: Nathan Sprague

"""
import urllib
from urllib.parse import urlencode
from urllib.request import urlopen
import json
import textwrap
from canvasapi import Canvas

API_KEY = "PUT_KEY_HERE"
COURSE_ID = "1962773"


def get_student_enrollment(course_id, student_id, key):
    url = f"https://canvas.jmu.edu/api/v1/courses/{course_id}/enrollments"
    header = {"Authorization": f"Bearer {key}"}
    form_data = {"user_id": student_id}
    data = urlencode(form_data).encode("utf-8")
    request = urllib.request.Request(url, data, headers=header, method="GET")
    return json.loads(urlopen(request).read())


class Enroller(object):
    def __init__(self, course_id, key):
        self.url = f"https://canvas.jmu.edu/api/v1/courses/{course_id}/enrollments"
        self.course_id = course_id
        self.key = key
        self.header = {"Authorization": f"Bearer {key}"}

    def delete_student(self, student_id):
        enrollment_id = get_student_enrollment(self.course_id, student_id, self.key)[0][
            "id"
        ]
        form_data = {"task": "delete"}
        data = urlencode(form_data).encode("utf-8")
        request = urllib.request.Request(
            self.url + f"/{enrollment_id}", data, headers=self.header, method="DELETE"
        )
        urlopen(request)

    def add_student(self, student_id):
        form_data = {}

        form_data["enrollment[user_id]"] = student_id
        form_data["enrollment[type]"] = "StudentEnrollment"
        form_data["enrollment[enrollment_state]"] = "active"
        form_data["enrollment[notify]"] = "false"

        data = urlencode(form_data).encode("utf-8")
        request = urllib.request.Request(self.url, data, headers=self.header)
        urlopen(request)


def main():
    canvas = Canvas("https://canvas.jmu.edu", API_KEY)
    course = canvas.get_course(COURSE_ID)

    # desired_ids = set(["5708837", "5882385", "5796181", "5786152",
    #                    "5789835", "5785370", "5802453", "5698825",
    #                    "5712368", "5807329", "5801893", "5792724",
    #                    "5879770", "5885733", "5801358", "5848998",
    #                    "5890356", "5800420", "5850731", "5801334",
    #                    "5686961", "5888089", "5802860", "5794877",
    #                    "5789423", "5802549", "5799814", "5710736",
    #                    "5797955", "5800127", "5789417", "5792295",
    #                    "5880095", "5755692", "5891575", "5883163",
    #                    "5778508", "5537248", "5805743", "5795163",
    #                    "5795157", "5792341", "5885034", "5789299",
    #                    "5802630", "5709094", "5799231", "5673260",
    #                    "5884375", "5890365", "5614994", "5802864",
    #                    "5801593", "5799160", "5801915", "5713587",
    #                    "5792686", "5802061"])

    desired_ids = set(["4145230"])

    current_ids = set()
    users = course.get_users(enrollment_type=["student"])
    names = {}
    for user in users:
        names[str(user.id)] = user.name
        current_ids.add(str(user.id))

    to_remove = current_ids - desired_ids
    to_add = desired_ids - current_ids

    gp = Enroller(COURSE_ID, API_KEY)

    if len(to_remove) > 0:
        names_string = textwrap.wrap(", ".join(names.values()))
        names_string = "\n  ".join(names_string)
        print(f"About to remove the following students:\n  {names_string}")
        ok = input("OK? (Y/n): ")
        if len(ok) == 0 or ok.lower().startswith("y"):
            for cur in to_remove:
                print("removing", names[cur])
                gp.delete_student(cur)

    if len(to_add) > 0:
        ids_string = textwrap.wrap(", ".join(list(to_add)))
        ids_string = "\n  ".join(ids_string)
        print(f"About to add the following students:\n  {ids_string}")
        ok = input("OK? (Y/n): ")
        if len(ok) == 0 or ok.lower().startswith("y"):
            for cur in to_add:
                print("adding", cur)
                gp.add_student(cur)


if __name__ == "__main__":
    main()
