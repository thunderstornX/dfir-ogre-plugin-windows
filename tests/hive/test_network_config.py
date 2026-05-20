import json
import os
from unittest import TestCase

from dfir_ogre_common import Metadata, OutputConfiguration, RunConfiguration

from dfir_ogre_plugin_windows import RegNetworkConfig

from . import CONF_FOLDER, TEMP_FOLDER

DATA_FOLDER = os.path.join("tests", "data")
os.makedirs(TEMP_FOLDER, exist_ok=True)


class NetworkConfig(TestCase):
    # python -m unittest tests.hive.test_network_config.NetworkConfig.test_network_config -v
    def test_network_config(self):
        plugin_file = os.path.join(CONF_FOLDER, "network_configuration.xml")
        input_file = os.path.join(DATA_FOLDER, "hive", "SYSTEM.dat")

        base_output_name = "network_config"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".network_config.jsonl"
        )
        if os.path.exists(output_file):
            os.remove(output_file)

        output_config = OutputConfiguration(
          base_output_name,
          TEMP_FOLDER,
          with_timeline=True,
          with_qualifiers=True,
          include_empty=False,
        )
        run_config = RunConfiguration([output_config])

        metadata = Metadata("test")
        parser = RegNetworkConfig()
        self.assertEqual("RegNetworkConfig", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 6
        lines = report.output_reports[0].file_reports[0].num_lines
        self.assertEqual(lines, expected_lines)

        filename = report.output_reports[0].file_reports[0].file_name
        self.assertEqual(filename, output_file)

        with open(output_file) as fp:
            i = 0

            for line in fp:
                js = json.loads(line)
                if i == 1:
                    js["description"] = "dhcp_enabled: false - ip_address: 10.1.7.1"
                    js["additional_description"] = (
                        "network_mask: 255.0.0.0 - gateway: 10.0.0.2"
                    )
                i += 1
            self.assertEqual(i, expected_lines)
