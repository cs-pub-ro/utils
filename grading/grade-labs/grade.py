#! /usr/bin/env python3


import argparse
from os.path import exists
from json import load
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
REGISTER_CONFIG_FILE = "course_registers.json"
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def _get_args():
    """
    Parses and returns the command-line arguments.
    """
    parser = argparse.ArgumentParser("Reads students' names from an " + \
        "attendance sheet (Google Sheets) and writes their grades to the " +\
        "class config")
    parser.add_argument("-l", "--lab", dest="lab_no", type=int, required=True,
        help="Lab number")
    parser.add_argument("-t", "--ta", dest="ta", type=str, required=False,
        help="TA acronym")
    parser.add_argument("-c", "--course", dest="course", type=str, required=True,
        help="The acronym of the course in whose config to write the grades.")

    return parser.parse_args()


def _login():
    """
    Performs TA login using the token.json file, if present.
    Otherwise, it uses credentials.json.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE,
                SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE, "w", encoding='ascii') as token:
            token.write(creds.to_json())

    return build("sheets", "v4", credentials=creds)


def _get_ranges(service, spreadsheet_id, sheet_name, ids_col, grades_col):
    """
    Returns the values in the given range of the given sheet.
    """
    ranges = [f"{sheet_name}!{ids_col}", f"{sheet_name}!{grades_col}"]
    grades = service.spreadsheets().values().batchGet(
        spreadsheetId=spreadsheet_id, ranges=ranges).execute()

    stud_names = grades["valueRanges"][0]["values"]
    stud_grades = grades["valueRanges"][1].get("values", [])
    stud_grades += [[]] * (len(stud_names) - len(stud_grades))

    return list(zip(stud_names, stud_grades))


def _get_attendees(service, config, lab_no):
    """
    Returns a list of tuples made up of lab attendees' IDs and their
    grades.
    """
    all_sheets = service.spreadsheets().get(
        spreadsheetId=config["attendance_id"]).execute().get('sheets', '')

    for sheet in all_sheets:
        if f"Lab {lab_no}" in sheet["properties"]["title"] \
                or f"Lab{lab_no:02d}" in sheet["properties"]["title"]:
            sheet_name = sheet["properties"]["title"]
            break

    attend_ranges = _get_ranges(service, config["attendance_id"], sheet_name,
        config["attendance_ids_col"], config["attendance_grade_col"])
    print("done printing")
    return [(ent[0][0], ent[1][0])
        for ent in filter(lambda s: s[0][0] != "#N/A", attend_ranges)]


def _get_register_range(service, config, lab_sheet, lab_no):
    """
    Returns the following dictionary:
        - keys = students' IDs
        - values = tuple(index in the grades list, grade)
    """
    register_ranges = _get_ranges(service, config["register_id"], lab_sheet,
        config["register_ids_col"], config["register_grade_cols"][lab_no])
    return { k[0]: (v, i) for i, (k, v) in enumerate(register_ranges) }


def _make_value_range(sheet, col, idx, value):
    """
    Returns one ValueRange object that writes the given value at col[idx].
    """
    pos = col.find(":")
    # TODO: [Bug] This assumes actual grades start from a row < 10.
    # This holds true for most registers, though.
    col_start = int(col[pos - 1 : pos])
    col = col[pos + 1 :]

    return {
        "range": f"{sheet}!{col}{col_start + idx}",
        "majorDimension": "ROWS",
        "values": [[value]]
    }


def main(course, lab_no, ta):
    """
    Retrieves the attendance list and grades all studens who haven't been
    already graded. Also assigns the TA to the subgroup if the ta parameter is
    specified.
    """
    service = _login()
    with open(REGISTER_CONFIG_FILE, "r", encoding='ascii') as config_file:
        config = load(config_file)[course]

    # Read students who participated in the lab.
    students_lab = _get_attendees(service, config, lab_no)

    # The skeleton of the request body.
    body = {
        "valueInputOption": "USER_ENTERED",
        "data": [ ],
        "includeValuesInResponse": False
    }

    # Look for the students in all sheets.
    for sheet in config["register_sheets"]:
        reg_range = _get_register_range(service, config, sheet, lab_no)

        if any(map(lambda s: len(s) < 2, students_lab)):
            print("You have at least one student that it's not graded in"
            "attendance list. Please grade all students before run the script.")
            return

        for stud, grade in students_lab:
            if stud in reg_range and len(reg_range[stud][0]) == 0:
                body["data"].append(_make_value_range(sheet,
                    config["register_grade_cols"][lab_no], reg_range[stud][1], grade))
                if ta:
                    body["data"].append(_make_value_range(sheet,
                        config["ta_col"], reg_range[stud][1], ta))
            elif stud in reg_range:
                print(f"Error: student '{stud}' has already been graded for lab {lab_no}.")

    # Send the update request.
    response = service.spreadsheets().values().batchUpdate(
        spreadsheetId=config["register_id"], body=body).execute()

    print(f"Class register: https://docs.google.com/spreadsheets/d/{config['register_id']}")

    # Print the results.
    updated_cells = response.get("totalUpdatedCells", 0)
    if (not ta and updated_cells == len(students_lab)) \
            or (ta and updated_cells == 2 * len(students_lab)):
        print("All students are graded!")
    elif updated_cells != 0:
        print(f"Modified {updated_cells} cells:")
        for resp in response["responses"]:
            print(resp["updatedRange"])
    else:
        print("No cells modified!")


if __name__ == "__main__":
    args = _get_args()
    main(args.course, args.lab_no, args.ta)
