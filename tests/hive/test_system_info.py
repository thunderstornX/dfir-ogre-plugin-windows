import json
import os
from unittest import TestCase

from dfir_ogre_common import BatchEntry, Metadata, OutputConfiguration, RunConfiguration

from dfir_ogre_plugin_windows import RegSystemInfo

from . import CONF_FOLDER, TEMP_FOLDER

DATA_FOLDER = os.path.join("tests", "data")
os.makedirs(TEMP_FOLDER, exist_ok=True)


class TestRegSystemInfo(TestCase):
    # python -m unittest tests.hive.test_system_info.TestRegSystemInfo.test_system_info -v
    def test_system_info(self):
        plugin_file = os.path.join(CONF_FOLDER, "reg_system_info.xml")

        metadata = Metadata("test")
        metadata.vss ="test_vss"
        software_file = os.path.join(DATA_FOLDER, "hive", "SOFTWARE_W10")
        system_file = os.path.join(DATA_FOLDER, "hive", "SYSTEM_W10")

        base_output_name = "reg_system_info"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".reg_systeminfo.jsonl"
        )
        if os.path.exists(output_file):
            os.remove(output_file)

        output_config = OutputConfiguration(
          base_output_name,
          TEMP_FOLDER,
          with_timeline=False,
                    include_empty=True,
        )

        run_config = RunConfiguration([output_config])

        entries = []
        entries.append(BatchEntry(software_file,run_config,metadata))
        entries.append(BatchEntry(system_file,run_config,metadata))

        parser = RegSystemInfo()
        self.assertEqual("RegSystemInfo", parser.description().command)  # type: ignore

        report = parser.parse(entries, plugin_file)
        self.assertEqual(None, report.last_error)

        expected_lines = 1
        lines = report.output_reports[0].file_reports[0].num_lines
        self.assertEqual(lines, expected_lines)

        filename = report.output_reports[0].file_reports[0].file_name
        self.assertEqual(filename, output_file)

        with open(output_file) as fp:
            i = 0
            for line in fp:
                jsoned = json.loads(line)

                self.assertEqual(
                    jsoned["product_name"],
                    "Windows 10 Enterprise",
                )
                self.assertEqual(jsoned["os_version"], "10.0")
                self.assertEqual(jsoned["build_number"], "18362")
                self.assertEqual(jsoned["install_date"], "2019-07-18T15:33:26.000000+00:00")
                self.assertEqual(jsoned["architecture"], "AMD64")
                self.assertEqual(len(jsoned["interfaces"]), 13)


                i += 1
            self.assertEqual(i, expected_lines)
