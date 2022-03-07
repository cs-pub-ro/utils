# Anonymizing Gradebooks

This is a guide for anonymizing gradebooks, i.e. showing the grades publicly but with no references to student names.
Generally, this is required when the gradebook is stored in a spreadsheet-like document (Google Sheets included).

The end goal is to make it very easy for a teaching team to have:
1. a private version of the gradebook with names, groups and other private information and all the grades
1. a public version of the gradebook with the private information removed, i.e. only the grades available

The idea behind this is to have a unique identifier for each student.
The unique identifier mapping to each student is only available in the private version of the gradebook.
The unique identifier is part of the public version of the gradebook together with grades.
No reference to student names is publicly available.

## Get Unique Identifiers

The `unique_ids_10000.txt` in this folder stores `10000` unique identifiers of `12` characters each.
The required number of identifiers can be selected (and shuffled) from this file.

If you want to generate a different set of unique identifiers, you can:

* Use the https://pwgen.io/en/ website.
* Use the https://www.pwdgen.org/ website.
* Use the [pwgen](https://linux.die.net/man/1/pwgen) command line tool.
  For example, to generate `150` identifiers of `12` characters each, use:

  ```bash
  $ pwgen -0 -1 12 150
  aeShoihaisue
  Kaiphuewaihu
  Poofeezuquai
  IezeiLoophaN
  Ooshoowoosaa
  [...]
  ```

  The `pwgen` tool was used to generate the `unique_ids_10000.txt` file.

## Create the Private Gradebook

The private gradebook will store the private identification information: student, email, group, teaching assistant.
This information is provided internally by the university for each class.
It may be either through the secretariat or through a university platform such as [Moodle at UPB](https://curs.upb.ro/).

Assuming the private gradebook is stored in spreadsheet document, make sure there are columns for
* the private identification information: student, email, group, teaching assistant
* the unique identifier
* the grades (per class topic, including formulas)

Fill the private gradebook with the private information and add formulas for grades.

Add the unique identifiers in the corresponding column.
Now the private class register contains the mapping between the private identification information and the unique identifier.

### Notes Mapping Students to Identifiers

Each class has its own student-to-id mapping, so the same identifiers can be used for different classes.
Even classes with the same students can use the same identifiers provided they are shuffled before doing a mapping to students, i.e. before filling the unique identifier column in the private gradebook.

## Generate the Public Gradebook

The public gradebook will be generated as a sheet in the private gradebook document or as private document.
Then, the public information in the private gradebook (unique identifiers and grades) will be linked in the public document.

The easiest way is to create a different public sheet in the private gradebook and add formulas that shows, for each cell of the public sheet, the contents of the private sheet.

## Demo using Google Sheets

[Here](https://docs.google.com/spreadsheets/d/1QOO3HbTEJY70U3IjPkEpw3G_U8TCBfX5RIx6RJkf2zI/edit?usp=sharing) is a demo of using Google Sheets for storing a private / public gradebook.
There are 10 sheets, 5 private and 5 public.
Each public sheet uses formulas to fill its cells with the public information in the corresponding private sheet: unique identifier and grades.
Additionally, public sheets are protected to prevent accidentally modification;
all updates should only happen in the private sheets.

By using `File -> Share -> Publish` to the web in the Google document, we publish each public sheet (all 5 sheets).
This results in the class register being publicly available [here](https://docs.google.com/spreadsheets/d/e/2PACX-1vRxo6bv-PerDoeGJzRwAAmZdbjlISUf3qZQ52waqyq5dx5csYosnu3S9peS5q9BWP5oiI9EMz_EqTFk/pubhtml).
Note that the link for each sheet has an `?gid=...&single=true` suffix;
remove that and all public sheets are available.

### Improving Anonymity

To improve anonymity, sort entries in public sheets by the identifier.
This will remove the possibility for students to infer their name by their place in the official class register.

Sorting entries is done by selecting the range in the spreadsheet document and sorting it by the unique identifier column.

### Send Unique Identifiers to Students

Students have to be privately delivered their unique identifiers. This can be done either by mail or by creating an assignment on the course page. 

### mail

We recommend you use the [send-mail set of Python scripts](https://github.com/systems-cs-pub-ro/utils/tree/master/send-email) for that.
You will create a CSV file with four columns: `firstname`, `lastname`, `email`, `identifier`.
Compose a generic templated message and use the `$identifier` construct to have it replaced with the per-student identifier.

Use the sample message in the `message.txt` file in this folder.

### Assignment

To add UUID as feedback for an Assignment activity:

* From course page, go `Turn editing on` -> `Add an activity or resource` -> `Assignment` -> `UUID` and:

    * untick  **all** ticks from `Availability`.
    * untick `Online text` and `File submission` from `Submission types` 
    * Feedback types bife **only** pentru `Feedback comments` and `Offline grading worksheet`.


* From Moodle, click on activity `UUID` -> `Settings` -> `View all submissions` -> `Grading action` ... `Download grading worksheet`, which downloads a csv.

*  Locally, open the csv -> modify **only** the column `Feedback comments` with `UUID-ul`-> `Save`

* From Moodle, click on activity `UUID` -> `Settings` -> `View all submissions` -> `Grading action` ... `Upload grading worksheet` -> choose the modified csv-> verify the mapping between code and student -> `Confirm`.
