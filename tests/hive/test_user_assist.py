import json
import os
from unittest import TestCase

from dfir_ogre_common import Metadata, OutputConfiguration, RunConfiguration

from dfir_ogre_plugin_windows import RegUserAssist

from . import CONF_FOLDER, TEMP_FOLDER

DATA_FOLDER = os.path.join("tests", "data")
os.makedirs(TEMP_FOLDER, exist_ok=True)


class TestUserAssist(TestCase):
    # python -m unittest tests.hive.test_user_assist.TestUserAssist.test_user_assist -v
    def test_user_assist(self):
        plugin_file = os.path.join(CONF_FOLDER, "user_assist.xml")

        input_file = os.path.join(DATA_FOLDER, "hive", "NTUSER.dat")

        base_output_name = "user_assist"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".user_assist.jsonl"
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
        parser = RegUserAssist()
        self.assertEqual("RegUserAssist", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 31
        lines = report.output_reports[0].file_reports[0].num_lines
        self.assertEqual(lines, expected_lines)

        filename = report.output_reports[0].file_reports[0].file_name
        self.assertEqual(filename, output_file)

        with open(output_file) as fp:
            i = 0
            for line in fp:
                jsoned = json.loads(line)
                if i == 1:
                    self.assertEqual(
                        jsoned["description"],
                        "program_name: Microsoft.Getstarted_8wekyb3d8bbwe!App",
                    )
                    self.assertEqual(
                        jsoned["additional_description"],
                        "run: 14",
                    )

                i += 1
            self.assertEqual(i, expected_lines)
