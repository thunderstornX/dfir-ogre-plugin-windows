import json
import os
from unittest import TestCase

from dfir_ogre_common import Metadata, OutputConfiguration, RunConfiguration

from dfir_ogre_plugin_windows import RegUserProfile

from . import CONF_FOLDER, TEMP_FOLDER

DATA_FOLDER = os.path.join("tests", "data")
os.makedirs(TEMP_FOLDER, exist_ok=True)


class UserProfile(TestCase):
    # python -m unittest tests.hive.test_user_profile.UserProfile.test_user_profile -v
    def test_user_profile(self):
        plugin_file = os.path.join(CONF_FOLDER, "user_profile.xml")

        input_file = os.path.join(DATA_FOLDER, "hive", "SOFTWARE.dat")

        base_output_name = "user_profile"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".user_profile.jsonl"
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

        metadata = Metadata("test")
        parser = RegUserProfile()
        self.assertEqual("RegUserProfile", parser.description().command)  # type: ignore

        run_config = RunConfiguration([output_config])
        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 7
        lines = report.output_reports[0].file_reports[0].num_lines
        self.assertEqual(lines, expected_lines)

        filename = report.output_reports[0].file_reports[0].file_name
        self.assertEqual(filename, output_file)

        with open(output_file) as fp:
            i = 0

            for line in fp:
                js = json.loads(line)
                if i == 0:
                    self.assertEqual(js["related_user"], "S-1-5-18")
                    self.assertEqual(
                        js["description"],
                        "path: %systemroot%\\system32\\config\\systemprofile",
                    )
                    self.assertEqual(
                        js["additional_description"],
                        "user_name: systemprofile",
                    )
                i += 1
            self.assertEqual(i, expected_lines)
