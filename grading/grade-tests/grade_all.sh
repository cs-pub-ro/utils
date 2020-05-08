#!/bin/sh

set -u

if [ $# -ne 4 ]; then
    echo "Usage: $0 <csv_dir> <exam_classes> <exam_numbers> <field_separator>"                        >&2
    echo "Example: $0 . 'CA CB CC' \"\$(seq 2 5)\" ','"                                               >&2
    echo "Exam results files must contain the class and number in it, and must be the ONLY such file" >&2
    echo "Example: L-A3-S2-SO-CA-Test de curs 2...csv"                                                >&2
    exit 1
fi

SCRIPT=$(readlink -f $0)
SCRIPT_DIR="${SCRIPT%/*}"
TMP_DIR=$(mktemp -d "${SCRIPT_DIR}/tmp.XXXXXX")

CSV_DIR="${1}"
CLASSES="${2}"
EXAM_NUMS="${3}"
FS="${4}"

if [ ! -d "${CSV_DIR}" ]; then
    echo "First parameter is not a directory!"                                                        >&2
    exit 2
fi

mkdir -p "${TMP_DIR}"

for N in ${EXAM_NUMS}; do
    RESULT_FILE="${TMP_DIR}/Test ${N}"
    rm -f "${RESULT_FILE}"

    for S in ${CLASSES}; do
        CRT_FILE=$(find "${CSV_DIR}" -maxdepth 1 -type f -name "*${S}*${N}*")
        [ -z "${CRT_FILE}" ] && continue

        sed -e '/Nume,Prenume,"Adresă email",State,"Început la",Completat,"Timp încercare"/d' \
            -e '/"Medie generală"/d'                                                          \
            -e 's/^\xEF\xBB\xBF//'                                                            \
            -e 's/\r//g'                                                                      \
            "${CRT_FILE}" >> "${RESULT_FILE}"
    done
done

for N in ${EXAM_NUMS}; do [ -f "${TMP_DIR}/Test ${N}" ] && echo "'${TMP_DIR}/Test ${N}'"; done |
    xargs awk -v FPAT="([^${FS}]+)|(\"[^\"]+\")" -v sep="${FS}" '
BEGIN {
    header = "username"
    column_idx = 2
}

{
    if (FILENAME != file) {
        file = FILENAME
        split(file, file_parts, "/")
        column = file_parts[length(file_parts)]
        columns[column_idx++] = column
        header = header sep column
    }

    email = $3
    split(email, email_parts, "@")
    username = email_parts[1]
    grade = $8

    gsub(/,/, ".", grade)
    grades[username"|"column] = grade
    if (! (username in users))
        users[username] = username
}

END {
    print(header)

    nusers = asorti(users, users_sorted, "@ind_str_asc")
    for (i = 1; i <= nusers; i++) {
        username = users_sorted[i]
        line = username

        PROC_INFO["sorted_in"] = "@ind_num_asc"
        for (column in columns)
            line = line sep grades[username"|"columns[column]]

        print(line)
    }
}
'

STATUS=$?

rm -rf "${TMP_DIR}"

exit ${STATUS}
