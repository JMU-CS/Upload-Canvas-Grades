#! /usr/bin/env python
"""
Usage:
submit_form.py FORM_XML CANVAS_KEY [COURSE_ID]
"""

from xml.dom import minidom
import sys
import canvas_util
import re

COURSE_ID = "1340489"

def add_escapes(document, tag_name="grade"):
    """Hacky method to escape any special characters inside the <grade>
    tags.

    """

    before_pattern = "(.*?)<" + tag_name
    p = re.compile(before_pattern, re.DOTALL)
    m = p.match(document)

    result = m.group(1)
    pattern = '(<'+tag_name + '.*?>)(.*?)(</' +tag_name+'>)'

    p = re.compile(pattern, re.DOTALL)

    for m in p.finditer(document):
        result +=  m.group(1)
        inner = m.group(2)
        inner = inner.replace("&", "&amp;")
        inner = inner.replace("<", "&lt;")
        inner = inner.replace(">", "&gt;")
        inner = inner.replace("'", "&apos;")
        inner = inner.replace('"', "&quot;")
        result += inner
        result += m.group(3) + "\n\n"

    result += "</assignment>"
    return result

def main():

    if len(sys.argv) < 3  :
        print "Usage: submit_form.py FORM_XML CANVAS_KEY [COURSE_ID]"
        sys.exit(0)

    if len(sys.argv) == 4:
        COURSE_ID = sys.argv[3]

    handle = open(sys.argv[1], 'r')
    document = handle.read()
    document = add_escapes(document)

    dom = minidom.parseString(document)

    assignment = dom.getElementsByTagName('assignment')[0]
    assignment_id = assignment.getAttribute('id')

    grade_elements = dom.getElementsByTagName('grade')

    gp = canvas_util.GradePoster(COURSE_ID, assignment_id, sys.argv[2])

    for grade in grade_elements:
        canvas_id = grade.getAttribute('canvas_id')
        score = grade.getAttribute('score')
        comment = grade.childNodes[0].data
        gp.post_grade_update(canvas_id, score, comment)

if __name__ == "__main__":
    main()
