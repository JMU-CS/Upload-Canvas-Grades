#! /usr/bin/env python
"""Generate an XML form from Canvas and Gradescope csv files that can be
uploaded to Canvas.

This script can be used when a single Canvas grade should be the sum
of multiple Gradescope grades.

Author: Nathan Sprague + Phil Riley
Version: 1/27/2022

"""
import argparse
import generate_form
import re
import os
import math

LATE_SLACK = .01 # about 14 minutes


def late_time_in_days(late_str):
    if len(late_str) == 0:
        return 0

    hours, mins, seconds = (int(s) for s in late_str.split(":"))
    return hours/24 + mins / 1440 + seconds / 86400
    
def days_late(late_str):

    late_time = late_time_in_days(late_str) - LATE_SLACK
    return int(math.floor(late_time + 1))


def gradescope_assignment_name(filename):
    """Extract the gradescope assessment name for an gradescope csv grade
    file name.

    """
    basename = os.path.basename(filename)
    m = re.search("(.*)_scores.csv", basename)
    if m:
        return m.group(1)
    return None

class GradescopeForm(generate_form.CanvasForm):

    def __init__(self, canvas_csv, assignment_id, gradescope_csvs,
                 late_penalty):

        super(GradescopeForm, self).__init__(canvas_csv, assignment_id, pad=True)

        self.student_dicts = [] # one dictionary per exercise/csv file
        self.table_headers = []
        self.ex_names = []
        self.late_penalty = late_penalty
        for gradescope_csv in gradescope_csvs:
            self.ex_names.append(gradescope_assignment_name(gradescope_csv))

            gradescope_table = generate_form.csv_to_numpy(gradescope_csv, pad=True)

            cur_headers = {}
            for col in range(gradescope_table.shape[1]):
                cur_headers[gradescope_table[0, col].strip(':')] = col
            self.table_headers.append(cur_headers)

            cur_entries = {}
            email_col = cur_headers['Email']
            for i in range(1, gradescope_table.shape[0], 1):
                eid = gradescope_table[i, email_col].split('@')[0]
                cur_entries[eid] = list(gradescope_table[i, :])
            self.student_dicts.append(cur_entries)




    def generate_comments(self, eid):
        comments = ""
        tool_score = 0
        try:
            table_data = zip(self.student_dicts, self.ex_names,
                             self.table_headers)
            for student_data, ex_name, table_headers in table_data:
                cur_score = student_data[eid][table_headers['Total Score']]
                
                late_str = student_data[eid][table_headers['Lateness (H:M:S)']]
                late = days_late(late_str)
                    
                comments += ex_name + ": "
                if cur_score == "not_submitted" or \
                   cur_score == "not_yet_submitted" or \
                   cur_score == '':
                    comments += "No Gradescope submission.\n"
                    cur_score = "0"
                elif late > 0 and self.late_penalty > 0:
                    multiplier = round(max(0, 1 - self.late_penalty * late), 2)
                    score = round(float(cur_score) * multiplier, 2)
                    comments += "{} x {} = {} (late)\n".format(cur_score,
                                                               multiplier,
                                                               score)
                    cur_score = score
                else:
                    comments += cur_score + "\n"

                tool_score += float(cur_score)
        except KeyError as e:
            # This may happen if a student is in Canvas, but not gradescope
            pass
        
        return comments, tool_score

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("canvas_csv", metavar="CANVAS_CSV")
    parser.add_argument("canvas_assignment_id",  metavar="CANVAS_ASSIGNMENT_ID")
    parser.add_argument("-l", "--late-penalty", type=float,
                        help="Late penalty per day (default .15)", default=.15)
    parser.add_argument("gradescope_csv", metavar="GRADESCOPE_CSV", nargs='*')
    args = parser.parse_args()
    wf = GradescopeForm(args.canvas_csv, args.canvas_assignment_id,
                        args.gradescope_csv, args.late_penalty)
    wf.generate_form()
