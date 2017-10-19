Utilities for offline Canvas and Web-CAT grading.  All scripts will
show usage information when executed with no arguments. Running with
the `-h` flag will show more detailed help information.

##   `generate_form.py`

This script generates a skeleton XML grade submission form from a
Canvas .csv grade file.

The generated forms will contain a `grade` element for each
student. The numeric score should be set in the `score` attribute.
Any grading comments should be placed between the open and close
`grade` tags.

```xml
	<grade name="STUDENT NAME" eid="student_eid" canvas_id="9999999"
	   score="27">

	  Any text here will show up as a grading comment in
	  Canvas. Newlines will be retained, but most other formatting
	  will be lost :(
	  
	  Nice work STUDENT NAME!
	  
	  TOTAL: 27/32

	</grade>
```

##   `generate_form_webcat.py`

This script generates an XML grade submission form that pulls data
from both a Canvas .csv grade file and a "Fully-detailed Web-CAT
CSV".

Example: 

```bash
$ ./generate_form_webcat.py 31_Jan_16_24_Grades-CS159_0005_SP17.csv \
  8459169 CS159-PA1C.csv -d '01/27/17 23:00PM' -s 10,1,2 > form.xml
```

##   `submit_form.py`

Script for uploading XML grading forms containing numeric grade
information and comments.

##   `canvas_util.py`

Utility code for posting grade information through the Canvas
API. No need to interact with this directly.
