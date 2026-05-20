import json
import os
from unittest import TestCase

from dfir_ogre_common import Metadata, OutputConfiguration, RunConfiguration

from dfir_ogre_plugin_windows import RecycleBin

from . import BASE_TEMP_FOLDER, CONF_FOLDER

DATA_FOLDER = os.path.join("tests", "data")
TEMP_FOLDER = os.path.join(BASE_TEMP_FOLDER, "recycle_bin")
os.makedirs(TEMP_FOLDER, exist_ok=True)


class TestRecycleBin(TestCase):
    # python -m unittest tests.test_recycle_bin.TestRecycleBin.test_windows7 -v
    def test_windows7(self):
        plugin_file = os.path.join(CONF_FOLDER, "recycle_bin.xml")
        input_file = os.path.join(DATA_FOLDER, "recycle_bin", "W7_$ILX8009")

        base_output_name = "recycle_bin_w7"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".recycle_bin.jsonl"
        )
        if os.path.exists(output_file):
            os.remove(output_file)

        output_config = OutputConfiguration(
          base_output_name,
          TEMP_FOLDER,
          with_timeline=True,
          with_qualifiers=True,
          include_empty=True,
        )
        run_config = RunConfiguration([output_config])

        metadata = Metadata("test")
        parser = RecycleBin()
        self.assertEqual("RecycleBin", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 1
        lines = report.output_reports[0].file_reports[0].num_lines
        self.assertEqual(lines, expected_lines)

        filename = report.output_reports[0].file_reports[0].file_name
        self.assertEqual(filename, output_file)

        with open(output_file) as fp:
            i = 0
            for line in fp:
                js = json.loads(line)
                if i == 0:
                    self.assertEqual(
                        js["description"],
                        "path: C:\\Users\\Admin\\Downloads\\prd-testzip-W7.zip",
                    )
                    self.assertEqual(
                        js["additional_description"],
                        "size: 572",
                    )

                i += 1
            self.assertEqual(i, expected_lines)

    # python -m unittest tests.test_recycle_bin.TestRecycleBin.test_windows10 -v
    def test_windows10(self):
        plugin_file = os.path.join(CONF_FOLDER, "recycle_bin.xml")
        input_file = os.path.join(DATA_FOLDER, "recycle_bin", "W10_$IC7V7S1")

        base_output_name = "recycle_bin_w10"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".recycle_bin.jsonl"
        )
        if os.path.exists(output_file):
            os.remove(output_file)

        output_config = OutputConfiguration(
          base_output_name,
          TEMP_FOLDER,
          with_timeline=True,
          with_qualifiers=True,
          include_empty=True,
        )
        run_config = RunConfiguration([output_config])
        metadata = Metadata("test")
        parser = RecycleBin()
        self.assertEqual("RecycleBin", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 1
        lines = report.output_reports[0].file_reports[0].num_lines
        self.assertEqual(lines, expected_lines)

        filename = report.output_reports[0].file_reports[0].file_name
        self.assertEqual(filename, output_file)

        with open(output_file) as fp:
            i = 0
            for line in fp:
                js = json.loads(line)
                if i == 0:
                    self.assertEqual(
                        js["description"],
                        "path: C:\\Users\\Administrator\\Downloads\\prd-testzip-W10.zip",
                    )
                    self.assertEqual(
                        js["additional_description"],
                        "size: 572",
                    )

                i += 1
            self.assertEqual(i, expected_lines)
