import json
import os
from unittest import TestCase

from dfir_ogre_common import Metadata, OutputConfiguration, RunConfiguration

from dfir_ogre_plugin_windows import RegServicesControlSet

from . import CONF_FOLDER, TEMP_FOLDER

DATA_FOLDER = os.path.join("tests", "data")
os.makedirs(TEMP_FOLDER, exist_ok=True)


class Services(TestCase):
    # python -m unittest tests.hive.test_services.Services.test_service_control_set -v
    def test_service_control_set(self):
        plugin_file = os.path.join(CONF_FOLDER, "services_control_set.xml")

        input_file = os.path.join(DATA_FOLDER, "hive", "SYSTEM.dat")

        base_output_name = "services"

        control_set_output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".services_control_set.jsonl"
        )
        if os.path.exists(control_set_output_file):
            os.remove(control_set_output_file)

        # firstboot_output_file = os.path.join(
        #     TEMP_FOLDER, base_output_name + ".firstboot.jsonl"
        # )
        # if os.path.exists(firstboot_output_file):
        #     os.remove(firstboot_output_file)

        output_config = OutputConfiguration(
          base_output_name,
          TEMP_FOLDER,
          with_timeline=True,
                    include_empty=False,
        )

        run_config = RunConfiguration([output_config])
        metadata = Metadata("test")
        parser = RegServicesControlSet()
        self.assertEqual("RegServicesControlSet", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 1389
        lines = report.output_reports[0].file_reports[0].num_lines
        self.assertEqual(lines, expected_lines)

        filename = report.output_reports[0].file_reports[0].file_name
        self.assertEqual(filename, control_set_output_file)

        with open(control_set_output_file) as fp:
            i = 0
            for line in fp:
                js = json.loads(line)
                if i == 64:
                    self.assertEqual(
                        js["description"],
                        "name: BITS - display_name: @%SystemRoot%\\system32\\qmgr.dll,-1000",
                    )
                    self.assertEqual(
                        js["additional_description"],
                        "service_type: Service WIN32 share process - start_type: Ondemand start - image_path: %SystemRoot%\\System32\\svchost.exe -k netsvcs -p - run_as: LocalSystem",
                    )
                    self.assertEqual(
                        js["data"]["performance_library"],
                        "C:\\Windows\\System32\\bitsperf.dll",
                    )

                i += 1
            self.assertEqual(i, expected_lines)
