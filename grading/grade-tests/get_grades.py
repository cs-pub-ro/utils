#!/usr/bin/env python3

import sys
import csv


def main():
    if len(sys.argv) != 3:
        print("Usage: {} id-list test-results.csv".format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    f = open(sys.argv[1])
    id_list = [l.strip() for l in f.readlines()]
    f.close()

    # Get number of records.
    f = open(sys.argv[2], newline='')
    reader = csv.reader(f, delimiter=',', quotechar='"')
    row_count = sum(1 for row in reader)
    f.close()

    # Parse records.
    grades_dict = {}
    f = open(sys.argv[2], newline='')
    reader = csv.reader(f, delimiter=',', quotechar='"')
    for i, row in enumerate(reader):
        if i == 0 or i == row_count-1:
            continue
        _id = row[2].split('@')[0]
        grade = int(row[7].split(',')[0])
        grades_dict[_id] = grade

    # Print grades.
    for _id in id_list:
        if _id in grades_dict.keys():
            print("{},{}".format(_id, grades_dict[_id]))
        else:
            print("{},0".format(_id))


if __name__ == "__main__":
    sys.exit(main())
