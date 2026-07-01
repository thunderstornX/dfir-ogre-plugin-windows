import json
import os
from unittest import TestCase

from dfir_ogre_common import (
    Metadata,
    OutputConfiguration,
    RunConfiguration,
)

from dfir_ogre_plugin_windows import Csv

from . import BASE_TEMP_FOLDER, CONF_FOLDER

DATA_FOLDER = os.path.join("tests", "data")

TEMP_FOLDER = os.path.join(BASE_TEMP_FOLDER, "csv")
os.makedirs(TEMP_FOLDER, exist_ok=True)


class ObjectInfoTest(TestCase):
    """Tests for the GetObjInfo CSV parser."""

    # python -m unittest tests.test_object_info.ObjectInfoTest.test_object_info -v
    def test_object_info(self):
        plugin_file = os.path.join(CONF_FOLDER, "object_info.xml")
        input_file = os.path.join(DATA_FOLDER, "csv", "GetObjInfo.100.csv")

        base_output_name = "GetObjInfo.100"
        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".objinfo.jsonl"
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
        parser = Csv()

        run_configuration = RunConfiguration([output_config])
        report = parser.parse(input_file, plugin_file, run_configuration, metadata)

        self.assertEqual(None, report.last_error)

        lines = report.output_reports[0].file_reports[0].num_lines
        expected_lines = 100
        self.assertEqual(lines, expected_lines)

        filename = report.output_reports[0].file_reports[0].file_name
        self.assertEqual(filename, output_file)

        with open(output_file) as fp:
            i = 0
            for line in fp:
                jsoned = json.loads(line)

                # Test first data row - Mutant entry (PendingRenameMutex)
                if i == 0:
                    self.assertEqual(jsoned["computer_name"], "W2022")
                    self.assertEqual(
                        jsoned["operating_system"],
                        "Microsoft Windows Server 2016 Standard Edition (build 20348), 64-bit"
                    )
                    self.assertEqual(jsoned["object_type"], "Mutant")
                    self.assertEqual(jsoned["object_name"], "PendingRenameMutex")
                    self.assertEqual(jsoned["object_path"], "\\PendingRenameMutex")
                    self.assertEqual(jsoned.get("link_target", ""), "")
                    self.assertIsNone(jsoned.get("link_creation_time"))

                # Test Type entry (TmTm)
                if i == 1:
                    self.assertEqual(jsoned["computer_name"], "W2022")
                    self.assertEqual(jsoned["object_type"], "Type")
                    self.assertEqual(jsoned["object_name"], "TmTm")
                    self.assertEqual(jsoned["object_path"], "\\ObjectTypes\\TmTm")



                # Test SymbolicLink with LinkTarget and LinkCreationTime
                if i == 72:  # SystemRoot symbolic link
                    self.assertEqual(jsoned["object_type"], "SymbolicLink")
                    self.assertEqual(jsoned["object_name"], "SystemRoot")
                    self.assertEqual(jsoned["link_target"], "\\Device\\BootDevice\\Windows")
                    self.assertEqual(jsoned["link_creation_time"], "2025-03-24T02:12:33.500000+00:00")



                i += 1
            self.assertEqual(i, expected_lines)
