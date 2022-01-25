#! /usr/bin/env python
"""
Usage:
submit_form.py --inputFile FORM_XML --courseId COURSE_ID [-keyFile filename | -key key]
"""

from xml.dom import minidom
import sys
import canvas_util
import re
import argparse

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

def read_parms():
    parser = argparse.ArgumentParser(description='Submit Grades')

    parser.add_argument('--inputFile', action='store',
                        dest='form_filename', default="", required=True,
                        help='XML file of grades and comments')

    parser.add_argument('--courseId', action='store',type=int,
                        dest='course_id', default="", required=True,
                        help='Canvas course id')

    parser.add_argument('--keyFile', action='store',
                        dest='key_filename',
                        help='file that contains your Canvas key (oauth)')

    parser.add_argument('--key', action='store',
                        dest='key',
                        help='your Canvas key (oauth)')

    return parser.parse_args()

def read_key(filename):
    f = open(filename,"r");
    keyLines = f.readlines()
    return keyLines[0].rstrip()

def main():
    parms = read_parms()

    if parms.key is None and parms.key_filename is None:
        print('Must specify either a key or a key filename')
        sys.exit(0)

    if (parms.key_filename):
        key = read_key(parms.key_filename)
    else:
        key = parms.key

    handle = open(parms.form_filename, 'r')
    document = handle.read()
    document = add_escapes(document)

    dom = minidom.parseString(document)

    assignment = dom.getElementsByTagName('assignment')[0]
    assignment_id = assignment.getAttribute('id')

    grade_elements = dom.getElementsByTagName('grade')

    gp = canvas_util.GradePoster(parms.course_id, assignment_id, key)

    for grade in grade_elements:
        canvas_id = grade.getAttribute('canvas_id')
        score = grade.getAttribute('score')
        comment = grade.childNodes[0].data
        gp.post_grade_update(canvas_id, score, comment)

if __name__ == "__main__":
    main()
