import os
from unittest import TestCase

from dfir_ogre_common import Metadata, OutputConfiguration, RunConfiguration

from dfir_ogre_plugin_windows import RegRecentApp

from . import CONF_FOLDER, TEMP_FOLDER

DATA_FOLDER = os.path.join("tests", "data")
os.makedirs(TEMP_FOLDER, exist_ok=True)


# TODO find data to properly test recent app
class RecentApp(TestCase):
    # python -m unittest tests.hive.test_recent_app.RecentApp.test_recent_app -v
    def test_recent_app(self):
        plugin_file = os.path.join(CONF_FOLDER, "recent_app.xml")

        input_file = os.path.join(DATA_FOLDER, "hive", "NTUSER.dat")

        base_output_name = "recent_app"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".recent_app.jsonl"
        )
        if os.path.exists(output_file):
            os.remove(output_file)

        output_config = OutputConfiguration(
          base_output_name,
          TEMP_FOLDER,
          with_timeline=False,
                    include_empty=True,
        )

        metadata = Metadata("test")
        parser = RegRecentApp()
        self.assertEqual("RegRecentApp", parser.description().command)  # type: ignore

        configuration = RunConfiguration([output_config])
        report = parser.parse(input_file, plugin_file, configuration, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 0
        lines = report.output_reports[0].file_reports[0].num_lines
        self.assertEqual(lines, expected_lines)

        filename = report.output_reports[0].file_reports[0].file_name
        self.assertEqual(filename, output_file)

        # with open(output_file) as fp:
        #     i = 0
        #     num_field = 0
        #     line_number = 0
        #     for line in fp:
        #         js = json.loads(line)
        #         if len(js) > num_field:
        #             num_field = len(js)
        #             line_number = i
        #         i += 1
        #     self.assertEqual(i, expected_lines)
        #     print(f"largest line:{line_number + 1} num_field:{num_field}")
