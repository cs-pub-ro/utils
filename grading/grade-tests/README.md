# Get Grades

Extract grades from CSV file provided by Moodle. Use list of IDs in gradebook to match ID to grade. Those who are absent (i.e. are part of the class register but don't figure in the CSV file) get a 0.

You need to create a file with the Moodle IDs of each student, one per line.

Then for each test, extract the CSV results file from Moodle. Run the `get_grades.py` script using the list file and the CSV results file as arguments.

Sample run:

```
./get_grades.py so2-2019-2020_id-list.txt L-A4-S2-SOI-C3-Test\ Laborator\ 4\ -\ Device\ drivere\ în\ Linux-note.csv | cut -d',' -f2
```

We use `cut` to only extract the grades and copy paste themin the gradebook. If you want to have an ID to grade mapping (such as for making sure everything works) simply discard the use of `cut`:

```
./get_grades.py so2-2019-2020_id-list.txt L-A4-S2-SOI-C3-Test\ Laborator\ 4\ -\ Device\ drivere\ în\ Linux-note.csv
```
