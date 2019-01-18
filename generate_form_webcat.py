#! /usr/bin/env python
"""
Usage:
generate_form.py CANVAS_CSV CANVAS_ASSIGNMENT_ID WEBCAT_CSV
"""
from datetime import datetime
import sys
import math
import argparse
import pytz
import generate_form

FIRST_ROW = 6

# Web-CAT csv columns
USER = 1
SUB_NUMBER = 4
TIME = 5
CORRECTNESS = 6
STYLE = 7
TOTAL = 10

def load_webcat_data(webcat_csv):
    """ Create a dictionary that maps from eids to lists with webcat data"""
    table = generate_form.csv_to_numpy(webcat_csv, FIRST_ROW)

    data = {}
    for i in range(table.shape[0]):
        eid = table[i, USER].strip().lower()
        data[eid] = list(table[i, :])
    return data

def webcat_time_to_datetime(text):
    result = datetime.strptime(text.replace('Etc/', ''), '%Y-%m-%d %H:%M:%S %Z')
    result = pytz.timezone('GMT').localize(result)
    result = result.astimezone(pytz.timezone('US/Eastern'))
    return result

def time_to_datetime(text):
    result = datetime.strptime(text.replace('Etc/', ''), '%m/%d/%y %I:%M%p')
    result = pytz.timezone('US/Eastern').localize(result)
    return result


def days_late(submission_time, due_time):
    late_amount = submission_time - due_time
    late_time_in_days = late_amount.total_seconds() / 60 / 60 / 24
    penalty = ""
    late_time_in_days -= .01 # give them 14 minutes
    if submission_time > due_time and late_time_in_days > 0:
        penalty += "({} day(s) late.)".format(int(math.floor(late_time_in_days+1)))
    return penalty


def submission_penalty(num_submissions, penalties):
    penalty = 0
    if penalties is not None:
        over = max(0, num_submissions - penalties[0])
        penalty = (over // penalties[2]) * penalties[1]
    return penalty

class WebCatForm(generate_form.CanvasForm):

    def __init__(self, canvas_csv, assignment_id, webcat_csv,
                 date_string=None, penalties=None):
        super(WebCatForm, self).__init__(canvas_csv, assignment_id)
        self.webcat_csv = webcat_csv
        self.webcat_data = load_webcat_data(webcat_csv)
        if date_string is not None:
            self.due_date = time_to_datetime(date_string)
        else:
            self.due_date = None
        self.penalties = penalties

    def generate_comments(self, eid):
        comments = ""
        if eid not in self.webcat_data:
            comments += "No Web-CAT submission.\n"
            return comments, 0
        else:
                
            submission_time = webcat_time_to_datetime(self.webcat_data[eid][TIME])
            comments += "Submission Time: {}".format(\
                                                submission_time.strftime('%m/%d/%y %I:%M%p %Z'))

            if self.due_date is not None:
                comments += (" " * 8 +
                             days_late(submission_time, self.due_date))
            comments += "\n"

            tool_score = (float(self.webcat_data[eid][CORRECTNESS]) +
                          float(self.webcat_data[eid][STYLE]))

            comments += "\nTesting points:      {:.2f}\n".format(float(self.webcat_data[eid][CORRECTNESS]))
            comments += "Checkstyle points:   {:.2f}\n".format(float(self.webcat_data[eid][STYLE]))

            penalty = submission_penalty(int(self.webcat_data[eid][SUB_NUMBER]),
                                         self.penalties)
            if penalty > 0:
                tool_score -= penalty
                comments += "Submission penalty:  {}\n".format(-penalty)

            comments += "Tool Score:          {:.2f}\n".format(tool_score)
            return comments, tool_score

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("canvas_csv", metavar="CANVAS_CSV")
    parser.add_argument("canvas_assignment_id",  metavar="CANVAS_ASSIGNMENT_ID")
    parser.add_argument("webcat_csv", metavar="WEBCAT_CSV")
    parser.add_argument("-d", "--due", help="Due date e.g.'04/29/25 11:00PM'")
    parser.add_argument("-s", "--sub_penalty", help="Format: NUM_FREE,PENALTY,FOR_EACH \n" +
                        "For example  3,1,2 would mean 3 free submissions, with a 1 pt \n" +
                        "penalty for each 2 submissions over three."
    )
    args = parser.parse_args()
    penalties = None
    if args.sub_penalty is not None:
        penalties = [int(i) for i in args.sub_penalty.split(",")]
    wf = WebCatForm(args.canvas_csv, args.canvas_assignment_id, args.webcat_csv,
                    args.due, penalties)
    wf.generate_form()
