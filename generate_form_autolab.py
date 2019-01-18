#! /usr/bin/env python
"""Generate an XML form from Canvas and Autolab csv files that can be
uploaded to Canvas.

Currently only looks at the total score.

Author: Nathan Sprague
Version: 1/18/2018

"""
import argparse
import generate_form

class AutoLabForm(generate_form.CanvasForm):

    def __init__(self, canvas_csv, assignment_id, autolab_csv):
    
        super(AutoLabForm, self).__init__(canvas_csv, assignment_id)
        self.autolab_table = generate_form.csv_to_numpy(autolab_csv)

        self.table_headers = {}
        for col in range(self.autolab_table.shape[1]):
            self.table_headers[self.autolab_table[0,col].strip(':')] = col

        self.student_data = {}
        for i in range(1, self.autolab_table.shape[0], 1):
            eid = self.autolab_table[i, 0].split('@')[0]
            self.student_data[eid] = list(self.autolab_table[i, :])

    def generate_comments(self, eid):
        comments = ""
        tool_score = 0
        try:
            tool_score = self.student_data[eid][self.table_headers['Total']]
            if tool_score == "not_submitted":
                comments += "No Autolab submission."
                tool_score = "0"
        except KeyError as e:
            # This may happen if a student is in Canvas, but not autolab
            pass
        
        return comments, tool_score

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("canvas_csv", metavar="CANVAS_CSV")
    parser.add_argument("canvas_assignment_id",  metavar="CANVAS_ASSIGNMENT_ID")
    parser.add_argument("autolab_csv", metavar="AUTOLAB_CSV")
    args = parser.parse_args()
    wf = AutoLabForm(args.canvas_csv, args.canvas_assignment_id,
                     args.autolab_csv)                    
    wf.generate_form()
