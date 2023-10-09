# Lab Grading

This script can be used to copy student grades from a lab register (named "attendance sheet") to the general register used by a given class.
Both registers need to be Google Spreadsheets.
In both of them, students need to be identifiable by unique IDs, such as LDAP accounts.

The attendance spreadsheet needs to store one worksheet per lab.
The names of these worksheets need to contain the following string within their name: `Lab <lab_num>`.
Note that both `Lab 01` and `Lab 1` are accepted.

## Environment

First, you need to install a couple of packages that are listed in `requirements.txt` file.
You can install them locally by running:

```console
pip3 install -r requirements.txt
```

## Configuration

In order to run the script, you need to configure some files in this folder.

Update the `course-registers.json` file and replace the strings `"TODO"` with the IDs of the registers from the courses you teach.
You can find the ID in the URL of the spreadsheet.
More information can be found [here](https://developers.google.com/sheets/api/guides/concepts).

To interact with Google API you need to generate a OAuth2.0 token.
To do this for the first time we need to create a project on the Google Cloud platform.
More information about how you can create a new project [here](https://cloud.google.com/resource-manager/docs/creating-managing-projects).

After you create the project, you must generate an OAuth2.0 token following instructions from [here](https://support.google.com/cloud/answer/6158849?hl=en).
Download the corresponding `json` format for it save it in a new file named `credentials.json`, placed in this folder.

## Running

### Arguments

- -l/--lab <lab_number>
- -t/--ta <teaching_assistant>
- -c/--course <course_name> (The same from the `course_registers.json`)

### Example

Copy all grades for the second lab of the Operating Systems course:

```console
python3 grade.py -l 2 -c Operating-Systems
```
