#! /usr/bin/env python
"""
usage: submit_form.py [-h] [--course-id COURSE_ID] [--key-file KEY_FILE] [--key KEY] [-y] GRADE_FORM


Submit Grades. Course id and oauth key will be read from a config file
if not provided. The config file will be updated if they are provided.

positional arguments:
  GRADE_FORM            XML file of grades and comments

optional arguments:
  -h, --help            show this help message and exit
  --course-id COURSE_ID
                        Canvas course id
  --key-file KEY_FILE   file that contains your Canvas key (oauth)
  --key KEY             your Canvas key (oauth)
  -y, --yes             Automatic yes to prompts

"""

from xml.dom import minidom
import sys
import canvas_util
import re
import argparse
import configparser

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
    help_text = """ Submit Grades.  Course id and oauth key will be read from a config
    file if not provided.  The config file will be updated if they are
    provided."""
    parser = argparse.ArgumentParser(description=help_text)

    parser.add_argument("grade_form",  metavar="GRADE_FORM",
                        help='XML file of grades and comments')

    parser.add_argument('--course-id', help='Canvas course id')

    parser.add_argument('--key-file', 
                        help='file that contains your Canvas key (oauth)')

    parser.add_argument('--key', help='your Canvas key (oauth)')

    parser.add_argument('-y', '--yes', action='store_true',
                        help="Automatic yes to prompts")

    return parser.parse_args()

def read_key(filename):
    f = open(filename,"r");
    keyLines = f.readlines()
    return keyLines[0].rstrip()

def main():
    parms = read_parms()
    
    config_path = canvas_util.get_config('config.ini')

    config = configparser.ConfigParser()
    config.read(config_path)

    if parms.key is None and parms.key_file is None and 'key' not in config['DEFAULT']:
        
        print('No default key is cached. Must specify either a key or a key filename')
        sys.exit(0)

    update = False
    if parms.key_file is not None:
        config['DEFAULT']['key'] = read_key(parms.key_file)
        update = True
    elif parms.key is not None:
        config['DEFAULT']['key'] = parms.key
        update = True


    if parms.course_id is None and 'course_id' not in config['DEFAULT']:
        print('No default course id is cached. Must provide --course-id')
        sys.exit(0)

    if parms.course_id is not None:
        config['DEFAULT']['course_id'] = parms.course_id
        update = True

    if update:
        print(f"Updating {config_path}")
        with open(config_path, 'w') as configfile:
            config.write(configfile)
        

    handle = open(parms.grade_form, 'r')
    document = handle.read()
    document = add_escapes(document)

    dom = minidom.parseString(document)

    assignment = dom.getElementsByTagName('assignment')[0]
    assignment_id = assignment.getAttribute('id')

    grade_elements = dom.getElementsByTagName('grade')

    gp = canvas_util.GradePoster(config['DEFAULT']['course_id'], assignment_id,
                                 config['DEFAULT']['key'])

    assigment_info = canvas_util.get_assignment_info(config['DEFAULT']['course_id'],
                                                     assignment_id,
                                                     config['DEFAULT']['key'])
    course_info = canvas_util.get_course_info(config['DEFAULT']['course_id'],
                                              config['DEFAULT']['key'])


    print('About to upload: "{}" to "{}"'.format(assigment_info['name'],
                                             course_info['name']))

    if parms.yes is False:
        ok = input("OK? (Y/n): ")
        if len(ok) != 0 and not ok.lower().startswith("y"):
            sys.exit(0)

    for grade in grade_elements:
        canvas_id = grade.getAttribute('canvas_id')
        score = grade.getAttribute('score')
        comment = grade.childNodes[0].data
        gp.post_grade_update(canvas_id, score, comment)

if __name__ == "__main__":
    main()
