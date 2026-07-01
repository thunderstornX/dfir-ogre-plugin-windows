import json
import os
from unittest import TestCase

from dfir_ogre_common import Metadata, OutputConfiguration, RunConfiguration

from dfir_ogre_plugin_windows import RegSnapExclude

from . import CONF_FOLDER, TEMP_FOLDER

DATA_FOLDER = os.path.join("tests", "data")
os.makedirs(TEMP_FOLDER, exist_ok=True)


class SnapshotExclude(TestCase):
    # python -m unittest tests.hive.test_snapshot_exclude.SnapshotExclude.test_snapshot_exclude -v
    def test_snapshot_exclude(self):
        plugin_file = os.path.join(CONF_FOLDER, "snapshot_exclude.xml")

        input_file = os.path.join(DATA_FOLDER, "hive", "SYSTEM.dat")

        base_output_name = "snapshot_exclude"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".backup_exclude.jsonl"
        )
        if os.path.exists(output_file):
            os.remove(output_file)

        output_config = OutputConfiguration(
          base_output_name,
          TEMP_FOLDER,
          with_timeline=True,
                    include_empty=True,
        )
        run_config = RunConfiguration([output_config])

        metadata = Metadata("test")
        parser = RegSnapExclude()
        self.assertEqual("RegSnapExclude", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 44
        lines = report.output_reports[0].file_reports[0].num_lines
        self.assertEqual(lines, expected_lines)

        filename = report.output_reports[0].file_reports[0].file_name
        self.assertEqual(filename, output_file)

        with open(output_file) as fp:
            i = 0
            for line in fp:
                js = json.loads(line)
                if i == 1:
                    self.assertEqual(js["data"]["name"], "ETW")
                    self.assertEqual(js["data"]["type"], "FilesNotToBackup")

                i += 1
            self.assertEqual(i, expected_lines)
