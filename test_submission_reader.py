from unittest import TestCase
from submission_reader import read_submission, sheet_reader
import pandas
import tempfile


def modify_excel_file(input_file, temp_file, replace: tuple[str, str, str, str]):
    sheet, column, old, new = replace
    with pandas.ExcelWriter(temp_file) as writer:
        for read_sheet in ["Sequence", "Category", "Kit", "Submitter", "Assembly"]:
            df = sheet_reader(input_file, read_sheet)
            if sheet == read_sheet:
                df[column] = df[column].replace(old, new)

            df.to_excel(writer, index=False, sheet_name=read_sheet)


def add_rows_to_excel_file(input_file, temp_file, sheet, rows):
    with pandas.ExcelWriter(temp_file) as writer:
        for read_sheet in ["Sequence", "Category", "Kit", "Submitter", "Assembly"]:
            df = sheet_reader(input_file, read_sheet)
            if sheet == read_sheet:
                df = df._append(rows, ignore_index=True)

            df.to_excel(writer, index=False, sheet_name=read_sheet)


def remove_rows_from_excel_file(input_file, temp_file, sheet, row_indexes):
    with pandas.ExcelWriter(temp_file) as writer:
        for read_sheet in ["Sequence", "Category", "Kit", "Submitter", "Assembly"]:
            df = sheet_reader(input_file, read_sheet)
            if sheet == read_sheet:
                df: pandas.DataFrame = df.drop(row_indexes)
            df.to_excel(writer, index=False, sheet_name=read_sheet)


class TestSubmissionReader(TestCase):
    def test_example_submission_works(self):
        read_submission("example_submission/submission.xlsx")

    def test_submission_with_changed_value(self):
        # Change something, but it should still work
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
            modify_excel_file(
                "example_submission/submission.xlsx",
                temp_file.name,
                ("Sequence", "plasmid_name", "pYTK003", "blah"),
            )
            read_submission(temp_file.name)

    def test_submission_with_multiple_kits(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
            add_rows_to_excel_file(
                "example_submission/submission.xlsx",
                temp_file.name,
                "Kit",
                [["dummy", "dummy"]],
            )
            with self.assertRaises(Exception) as context:
                read_submission(temp_file.name)

            self.assertEqual(str(context.exception), "There should be only one kit")

    def test_submission_with_missing_completely(self):
        for sheet in ["Sequence", "Category", "Kit", "Submitter", "Assembly"]:
            with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
                nb_rows = len(sheet_reader("example_submission/submission.xlsx", sheet))
                remove_rows_from_excel_file(
                    "example_submission/submission.xlsx",
                    temp_file.name,
                    sheet,
                    list(range(nb_rows)),
                )
                with self.assertRaises(Exception):
                    read_submission(temp_file.name)

    def test_wrong_pmid(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
            modify_excel_file(
                "example_submission/submission.xlsx",
                temp_file.name,
                ("Kit", "pmid", "PMID:25871405", "PMID:0"),
            )
            with self.assertRaises(Exception) as context:
                read_submission(temp_file.name)

            self.assertIn("PMID PMID:0 does not exist", str(context.exception))

    def test_wrong_kit_url(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
            modify_excel_file(
                "example_submission/submission.xlsx",
                temp_file.name,
                (
                    "Kit",
                    "addgene_url",
                    "https://www.addgene.org/kits/moclo-ytk/",
                    "https://www.addgene.org/dummy",
                ),
            )
            with self.assertRaises(Exception) as context:
                read_submission(temp_file.name)

            self.assertIn(
                "Addgene URL https://www.addgene.org/dummy does not exist",
                str(context.exception),
            )

    def test_wrong_github_user(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
            modify_excel_file(
                "example_submission/submission.xlsx",
                temp_file.name,
                (
                    "Submitter",
                    "github_username",
                    "manulera",
                    "manuleramanuleramanulera",
                ),
            )
            with self.assertRaises(ValueError) as context:
                read_submission(temp_file.name)
            self.assertIn(
                "Github username manuleramanuleramanulera does not exist",
                str(context.exception),
            )

    def test_wrong_orcid(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
            modify_excel_file(
                "example_submission/submission.xlsx",
                temp_file.name,
                ("Submitter", "orcid", "0000-0002-8666-9746", "0000-0000-0000-0000"),
            )
            with self.assertRaises(Exception):
                read_submission(temp_file.name)

    def test_referencial_integrity(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
            modify_excel_file(
                "example_submission/submission.xlsx",
                temp_file.name,
                ("Sequence", "category", "1", "blah"),
            )
            with self.assertRaises(Exception) as context:
                read_submission(temp_file.name)

            self.assertIn('"blah" not in categories', str(context.exception))

            modify_excel_file(
                "example_submission/submission.xlsx",
                temp_file.name,
                ("Category", "id", "1", "blah"),
            )

            with self.assertRaises(Exception) as context:
                read_submission(temp_file.name)

            self.assertIn('"1" not in categories', str(context.exception))

            modify_excel_file(
                "example_submission/submission.xlsx",
                temp_file.name,
                (
                    "Assembly",
                    "fragment_order",
                    "1|2|3a||4|5|6|7|8",
                    "1|2|3a||4|blah|6|7|8",
                ),
            )

            with self.assertRaises(Exception) as context:
                read_submission(temp_file.name)

            self.assertIn('"blah" not in categories', str(context.exception))
