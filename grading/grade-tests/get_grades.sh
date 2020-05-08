#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Usage: $0 id-list test-results.csv" >&2
    exit 1
fi

ID_LIST=$(readlink -f "$1")
TEST_CSV=$(readlink -f "$2")

awk -v FPAT='([^,]+)|("[^"]+")' -v id_list="${ID_LIST}" '
{
    if (FILENAME == id_list) {
        students[$1] = NR
    } else {
        email = $3
        split(email, email_parts, "@")
        username = email_parts[1]
        grade = $8

        gsub(/"/, "", grade)
        grades[username] = grade + 0
    }
}

END {
    PROCINFO["sorted_in"] = "@val_num_asc"
    for (student in students)
        if (student in grades)
            print(student","grades[student])
        else
            print(student","0)
}
' "${ID_LIST}" "${TEST_CSV}"
