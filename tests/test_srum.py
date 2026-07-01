import glob
import json
import os
from unittest import TestCase

from dfir_ogre_common import Metadata, OutputConfiguration, RunConfiguration

from dfir_ogre_plugin_windows import Srum

from . import BASE_TEMP_FOLDER, CONF_FOLDER

DATA_FOLDER = os.path.join("tests", "data")
TEMP_FOLDER = os.path.join(BASE_TEMP_FOLDER, "srum")
os.makedirs(TEMP_FOLDER, exist_ok=True)


class SrumTest(TestCase):
    # python -m unittest tests.test_srum.SrumTest.test_srum -v
    def test_srum(self):
        plugin_file = os.path.join(CONF_FOLDER, "srum.xml")
        input_file = os.path.join(DATA_FOLDER, "srum", "SRUDB.dat")
        base_output_name = "srum_test"

        output_file = os.path.join(TEMP_FOLDER, base_output_name)

        for f in glob.glob(output_file + "*"):
            os.remove(f)

        output_config = OutputConfiguration(
          base_output_name,
          TEMP_FOLDER,
          with_timeline=False,
                    include_empty=True,
        )

        run_config = RunConfiguration(
            [output_config],
            True,
        )
        metadata = Metadata("test")
        parser = Srum()
        self.assertEqual("Srum", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)

        expected_lines = 1660
        lines = report.output_reports[0].file_reports[0].num_lines
        self.assertEqual(lines, expected_lines)

        filename = report.output_reports[0].file_reports[0].file_name

        with open(filename) as fp:
            i = 0
            for line in fp:
                jsoned = json.loads(line)
                if i == 3:
                    self.assertEqual(
                        jsoned["app_id"],
                        "!!svchost.exe!1972/12/14:16:22:50!1c364![LocalSystemNetworkRestricted] [WdiSystemHost]",
                    )
                i += 1
            self.assertEqual(i, expected_lines)
