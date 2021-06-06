#! /usr/bin/env python
"""
Usage:
generate_form.py CANVAS_CSV CANVAS_ASSIGNMENT_ID

Jun 2021 -- Changes to support export of grade csv from Canvas that has
possible points in rows 2 or 3 (1 or 2 counting from 0).
"""

import numpy as np
from datetime import datetime
import sys
import csv

def csv_to_numpy(file_name, skip_rows=0):
    handle = open(file_name, 'r')
    data = list(csv.reader(handle, delimiter=',', quotechar='"'))
    # remove empty rows:
    data = [row for row in data if len(row) > 0]
    csv_np = np.array(data[skip_rows:], dtype=str)
    if np.sum(csv_np[1,:] == "Muted") > 0:
        csv_np = np.delete(csv_np, (1), axis=0)
    return csv_np

def assignment_info(canvas_csv, assignment_id):
    """ return a (name, max_points) tuple for this assignment id """
    data = csv_to_numpy(canvas_csv)
    if data[1,0].strip() == "Points Possible":
        points_row = 1
    else:
        points_row = 2

    for i in range(data.shape[1]):
        if assignment_id in data[0, i]:
            return (data[0, i], float(data[points_row, i]))

    raise LookupError("No such assignment ID: {}".format(assignment_id))

def load_canvas_ids(canvas_csv):
    """ Create a dictionary that maps from eids to (name, canvas_id) tuples."""

    table = csv_to_numpy(canvas_csv)
    data = {}
    # if header is longer, start at 3 (instead of 2) Kevin Molloy change
    if table[1,0].strip() == "Points Possible":
      start_row = 2
    else:
      start_row = 3

    for i in range(start_row, table.shape[0]):
        data[table[i, 2]] = (table[i, 0], table[i, 1])
    return data

class CanvasForm(object):

    def __init__(self, canvas_csv, assignment_id):
        self.canvas_csv = canvas_csv
        self.assignment_id = assignment_id
        self.canvas_data = load_canvas_ids(self.canvas_csv)
        info = assignment_info(self.canvas_csv, self.assignment_id)
        self.assignment_name = info[0]
        self.max_score = info[1]

    def generate_comments(self, eid):
        """ Can be overridden in a subclass. """
        return "", 0

    def generate_form(self):

        print('<?xml version="1.0" encoding="UTF-8"?>\n')
        assignment_tag = '<assignment id="{}" name="{}" points_possible="{}">\n'
        assignment_tag = assignment_tag.format(self.assignment_id,
                                               self.assignment_name,
                                               self.max_score)
        print(assignment_tag)

        for eid in sorted(self.canvas_data):
            comments, score = self.generate_comments(eid)

            open_tag = '<grade name="{}" eid="{}" canvas_id="{}"\n  score="{}">'
            open_tag = open_tag.format(self.canvas_data[eid][0], eid.lower(),
                                       self.canvas_data[eid][1],
                                       score)
            print(open_tag)
            print(comments)

            print("</grade>\n")

        print("</assignment>")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        cf = CanvasForm(sys.argv[1], sys.argv[2])
        cf.generate_form()
    else:
        print("Usage: generate_form.py CANVAS_CSV CANVAS_ASSIGNMENT_ID")
