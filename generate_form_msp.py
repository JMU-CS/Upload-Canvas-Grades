#! /usr/bin/env python
"""Generate an XML form from Canvas and Autolab csv files that can be
uploaded to Canvas.

This script can be used when a single Canvas grade should be the sum
of multiple Autolab grades.

Author: Nathan Sprague
Version: 9/3/2019

"""
import argparse
import generate_form
import re

def autolab_assignment_name(filename):
    """Extract the autolab assessment name for an autolab csv grade
    file name.

    """
    m = re.search("(.*)_(.*)_[0-9]{12}.csv", filename)
    if m:
        return m.group(2)
    return None

class AutoLabForm(generate_form.CanvasForm):

    def __init__(self, canvas_csv, assignment_id, autolab_csvs):

        super(AutoLabForm, self).__init__(canvas_csv, assignment_id)

        self.student_dicts = [] # one dictionary per exercise/csv file
        self.ex_names = []
        for autolab_csv in autolab_csvs:
            self.ex_names.append(autolab_assignment_name(autolab_csv))

            autolab_table = generate_form.csv_to_numpy(autolab_csv)

            cur_entries = {}
            for i in range(1, autolab_table.shape[0], 1):
                eid = autolab_table[i, 0].split('@')[0]
                cur_entries[eid] = list(autolab_table[i, :])
            self.student_dicts.append(cur_entries)

        # Table headers should be the same for all autolab csv files.
        autolab_table = generate_form.csv_to_numpy(autolab_csvs[0])
        self.table_headers = {}
        for col in range(autolab_table.shape[1]):
            self.table_headers[autolab_table[0, col].strip(':')] = col


    def generate_comments(self, eid):
        comments = ""
        tool_score = 0
        try:
            for student_data, ex_name in zip(self.student_dicts, self.ex_names):
                cur_score = student_data[eid][self.table_headers['Total']]
                comments += ex_name + ": "
                if cur_score == "not_submitted" or \
                   cur_score == "not_yet_submitted":
                    comments += "No Autolab submission.\n"
                    cur_score = "0"
                else:
                    comments += cur_score + "\n"
                tool_score += float(cur_score)
        except KeyError as e:
            # This may happen if a student is in Canvas, but not autolab
            pass
        
        return comments, tool_score

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("canvas_csv", metavar="CANVAS_CSV")
    parser.add_argument("canvas_assignment_id",  metavar="CANVAS_ASSIGNMENT_ID")
    parser.add_argument("autolab_csv", metavar="AUTOLAB_CSV", nargs='*')
    args = parser.parse_args()
    wf = AutoLabForm(args.canvas_csv, args.canvas_assignment_id,
                     args.autolab_csv)                    
    wf.generate_form()
