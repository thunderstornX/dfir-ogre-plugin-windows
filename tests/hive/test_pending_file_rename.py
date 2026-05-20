import json
import os
from unittest import TestCase

from dfir_ogre_common import Metadata, OutputConfiguration, RunConfiguration

from dfir_ogre_plugin_windows import RegPendingRename

from . import CONF_FOLDER, TEMP_FOLDER

DATA_FOLDER = os.path.join("tests", "data")
os.makedirs(TEMP_FOLDER, exist_ok=True)


class PendingFile(TestCase):
    # python -m unittest tests.hive.test_pending_file_rename.PendingFile.test_pending_files -v
    def test_pending_files(self):
        plugin_file = os.path.join(CONF_FOLDER, "pending_file_rename.xml")

        input_file = os.path.join(DATA_FOLDER, "hive", "SYSTEM.dat")
        base_output_name = "pending_files"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".pending_rename.jsonl"
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
        parser = RegPendingRename()
        self.assertEqual("RegPendingRename", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 93
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
                        "old_name: \\??\\C:\\WINDOWS\\system32\\spool\\DRIVERS\\x64\\3\\New\\mxdwdrv.dll",
                    )
                    self.assertEqual(
                        js["additional_description"],
                        "new_name: \\??\\C:\\WINDOWS\\system32\\spool\\DRIVERS\\x64\\3\\mxdwdrv.dll",
                    )

                i += 1
