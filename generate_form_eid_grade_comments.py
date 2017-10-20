#!/usr/bin/env python

"""
Usage:
generate_form_eid_grade_comments.py CANVAS_CSV CANVAS_ASSIGNMENT_ID SIMPLE_CSV
SIMPLE_CSV should have columns: eid,score,comments
"""

import argparse
import generate_form

SIMPLE_CSV_FIRST_ROW = 1

# SIMPLE csv columns
USER = 0
TOTAL = 1
COMMENTS = 2


def load_simple_data(simple_csv):
    """Create a dictionary that maps from eids to lists with 'simple' data"""
    table = generate_form.csv_to_numpy(simple_csv, SIMPLE_CSV_FIRST_ROW)

    data = {}
    for i in range(table.shape[0]):
        eid = table[i, USER].strip().lower()
        data[eid] = list(table[i, :])
    return data


class SimpleForm(generate_form.CanvasForm):

    def __init__(self, canvas_csv, assignment_id, simple_csv,
                 date_string=None, penalties=None):
        super(SimpleForm, self).__init__(canvas_csv, assignment_id)
        self.simple_csv = simple_csv
        self.simple_data = load_simple_data(simple_csv)

    def generate_comments(self, eid):
        if eid not in self.simple_data:
            comments = "No Web-CAT submission.\n"
            return comments, 0
        else:
            comments = self.simple_data[eid][COMMENTS]
            return comments, self.simple_data[eid][TOTAL]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("canvas_csv", metavar="CANVAS_CSV")
    parser.add_argument("canvas_assignment_id", metavar="CANVAS_ASSIGNMENT_ID")
    parser.add_argument("simple_csv", metavar="SIMPLE_CSV")
    parser.add_argument("-d", "--due", help="Due date e.g.'04/29/25 11:00PM'")
    parser.add_argument("-s", "--sub_penalty", help="Format: NUM_FREE,PENALTY\
                        , FOR_EACH \n" + "For example  3,1,2 would mean 3 \
                        free submissions, with a 1 pt \n" +
                        "penalty for each 2 submissions over three.")
    args = parser.parse_args()
    penalties = None
    if args.sub_penalty is not None:
        penalties = [int(i) for i in args.sub_penalty.split(",")]
    wf = SimpleForm(args.canvas_csv, args.canvas_assignment_id,
                    args.simple_csv, args.due, penalties)
    wf.generate_form()
