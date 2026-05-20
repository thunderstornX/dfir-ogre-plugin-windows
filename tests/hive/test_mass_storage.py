import json
import os
from unittest import TestCase

from dfir_ogre_common import Metadata, OutputConfiguration, RunConfiguration

from dfir_ogre_plugin_windows import RegMassStorageSystem

from . import CONF_FOLDER, TEMP_FOLDER

DATA_FOLDER = os.path.join("tests", "data")


class TestMassStorage(TestCase):
    # python -m unittest tests.hive.test_mass_storage.TestMassStorage.test_system_mass_storage -v
    def test_system_mass_storage(self):
        plugin_file = os.path.join(CONF_FOLDER, "mass_storage_system.xml")

        input_file = os.path.join(DATA_FOLDER, "hive", "SYSTEM_WITH_STORAGE.dat")

        base_output_name = "mass_storage_system"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".mass_storage.jsonl"
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
        parser = RegMassStorageSystem()
        self.assertEqual("RegMassStorageSystem", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 5
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
                        "type: Disk - vendor: JetFlash - product: Transcend_16GB - instance_id: 23NPMBDVM3GMSLXI&0",
                    )

                i += 1
            self.assertEqual(i, expected_lines)
