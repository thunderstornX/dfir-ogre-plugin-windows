import json
import os
from unittest import TestCase

from dfir_ogre_common import Metadata, OutputConfiguration, RunConfiguration

from dfir_ogre_plugin_windows import RegSIPP

from . import CONF_FOLDER, TEMP_FOLDER

DATA_FOLDER = os.path.join("tests", "data")
os.makedirs(TEMP_FOLDER, exist_ok=True)


class SIPP(TestCase):
    # python -m unittest tests.hive.test_subject_interface_package.SIPP.test_sipp -v
    def test_sipp(self):
        plugin_file = os.path.join(CONF_FOLDER, "subject_interface_package.xml")
        input_file = os.path.join(DATA_FOLDER, "hive", "SOFTWARE.dat")

        base_output_name = "subject_interface_package"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".subject_interface_package.jsonl"
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
        parser = RegSIPP()
        self.assertEqual("RegSIPP", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 17
        lines = report.output_reports[0].file_reports[0].num_lines
        self.assertEqual(lines, expected_lines)

        filename = report.output_reports[0].file_reports[0].file_name
        self.assertEqual(filename, output_file)

        with open(output_file) as fp:
            i = 0
            for line in fp:
                js = json.loads(line)
                if i == 0:
                    self.assertEqual(js["description"], "name: MSIP")
                    self.assertEqual(
                        js["additional_description"],
                        "dll: C:\\Windows\\System32\\MSISIP.DLL - function_name: MsiSIPVerifyIndirectData - guid: 000c10f1-0000-0000-c000-000000000046",
                    )
                i += 1
            self.assertEqual(i, expected_lines)
