# Get Grades

Extract grades from CSV file provided by Moodle. Use list of IDs in gradebook to match ID to grade. Those who are absent (i.e. are part of the class register but don't figure in the CSV file) get a 0.

You need to create a file with the Moodle IDs of each student, one per line.

Then for each test, extract the CSV results file from Moodle. Run the `get_grades.sh` script using the list file and the CSV results file as arguments.

Sample run:

```
./get_grades.sh so2-2019-2020_id-list.txt L-A4-S2-SOI-C3-Test\ Laborator\ 4\ -\ Device\ drivere\ în\ Linux-note.csv | cut -d',' -f2
```

We use `cut` to only extract the grades and copy paste them in the gradebook. If you want to have an ID to grade mapping (such as for making sure everything works) simply discard the use of `cut`:

```
./get_grades.sh so2-2019-2020_id-list.txt L-A4-S2-SOI-C3-Test\ Laborator\ 4\ -\ Device\ drivere\ în\ Linux-note.csv
```

# Grade all - grade_all.sh

Extract grades from multiple CSV files provided by Moodle. The users in the output will be all users identified in any CSV file.

The script expects there could be more than one test to extract grades from, and more than one file per test; as such there are 4 parameters that must be passed to the script:

 * `csv_dir` - path to the directory where (all) CSV files are located. Can be `.` for the current directory.
 * `exam_classes` - a list of identifiers for classes, separated by spaces. Exactly one identifier in the list must be in the name of the CSV file. For example, to grade tests for classes 'CA', 'CB', and 'CC', use "CA CB CC".
 * `exam_numbers` - a list of test numbers to extract grades from, separated by spaces. Exactly one identifier in the list must in the name of a file. For example, to get grades from tests 5, 6, and 7, use "5 6 7".
 * `field_separator` - the field separator used when outputting the grades. For a comma-separated output, use ','.

CSV files are only differentiated by their names, and they must contain exactly one identifier from each `exam_classes` and `exam_numbers`, and must be the only file that matches the pattern - e.g., there cannot be two files named `CA-Test-2-a.csv` and `CA-Test-2-b.csv`, if the values of the fields contain `CA`, and `2`, respectively, since both files match both criteria.

The output is a list of values, separated by `field_separator`, where the first value is the username, followed by the grades for each test.

### Use example:

The `test-results` directory contains the following test result CSV files, for tests 6 and 7, for classes CA, CB and CC. The directory structure is:

```
L-A3-S2-SO-CA-Test de curs 6 - Planificare-note.csv
L-A3-S2-SO-CB-Test de curs 6 - Planificare-note.csv
L-A3-S2-SO-CC-Test de curs 6 - Planificare-note.csv
L-A3-S2-SO-CA-Test de curs 7 - Memoria virtuală-note.csv
L-A3-S2-SO-CB-Test de curs 7 - Memoria virtuală-note.csv
L-A3-S2-SO-CC-Test de curs 7 - Memoria virtuală-note.csv
```

To parse the files, the script would be run as:

```
sh ./grade_all.sh "test-results" "CA CB CC" "6 7" ","
```

The output is a table of comma-separated values, where the header is 'username,Test 6,Test 7', followed by lines containing the IDs of the students and their grades for tests 6 and 7. The tests where the students did not attend will be left blank. The list of students is sorted in alphabetical order.

If you want to make sure that all students are in the output (even those who did not participate in any of the tests), you could create an extra CSV file with the IDs of all students on the 3rd column, and pass it as test 0 (for example). You could then simply remove the column for test 0 in the result, and the students who did not attend any test will be listed without any grades.

### Limitations

The script expects the CSV files to have the student's e-mail address on the 3rd column and the total grade on the 8th column. If the fields shift, you must change the `email = $3` and `grade = $8` lines of the embedded `awk` script, so the index of the email / username, and the grade are properly extracted.

The files are expected to have a header that contains `'Nume,Prenume,"Adresă email",State,"Început la",Completat,"Timp încercare"`, and a footer that contains `"Medie generală"` that will be deleted. If the values in the header of the footer differ (possibly because of the language the CSV file was downloaded in), please change the text of the `sed` rules so these are properly removed.

The files are not properly identified in a template-like manner. The second and third parameter of the script have a pseudo-template motivation.
