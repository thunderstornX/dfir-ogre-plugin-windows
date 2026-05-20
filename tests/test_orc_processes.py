import json
import os
from unittest import TestCase

from dfir_ogre_common import Metadata, OutputConfiguration, RunConfiguration

from dfir_ogre_plugin_windows import Csv, OrcProcesses1

from . import BASE_TEMP_FOLDER, CONF_FOLDER

DATA_FOLDER = os.path.join("tests", "data")
TEMP_FOLDER = os.path.join(BASE_TEMP_FOLDER, "processes")
os.makedirs(TEMP_FOLDER, exist_ok=True)


class TestOrcProcesses(TestCase):
    # python -m unittest tests.test_orc_processes.TestOrcProcesses.test_process_1 -v
    def test_process_1(self):
        plugin_file = os.path.join(CONF_FOLDER, "orc_processes_1.xml")
        input_file = os.path.join(DATA_FOLDER, "processes", "processes1.csv")
        base_output_name = "processes1"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".processes_orc.jsonl"
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
        parser = OrcProcesses1()
        self.assertEqual("OrcProcesses1", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 22
        lines = report.output_reports[0].file_reports[0].num_lines
        self.assertEqual(lines, expected_lines)

        filename = report.output_reports[0].file_reports[0].file_name

        self.assertEqual(filename, output_file)

        with open(output_file) as fp:
            i = 0
            for line in fp:
                js = json.loads(line)
                if i == 21:
                    self.assertEqual(
                        js["description"],
                        "name: PSEXESVC.exe",
                    )
                    self.assertEqual(
                        js["additional_description"],
                        "executable_path: C:\\WINDOWS\\PSEXESVC.exe - command_line: C:\\WINDOWS\\PSEXESVC.exe",
                    )
                i += 1
            self.assertEqual(i, expected_lines)

    # python -m unittest tests.test_orc_processes.TestOrcProcesses.test_process_2 -v
    def test_process_2(self):
        plugin_file = os.path.join(CONF_FOLDER, "orc_processes_2.xml")
        input_file = os.path.join(DATA_FOLDER, "processes", "processes2.csv")
        base_output_name = "processes2"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".processes_orc.jsonl"
        )
        if os.path.exists(output_file):
            os.remove(output_file)

        output_config = OutputConfiguration(
          base_output_name,
          TEMP_FOLDER,
          with_timeline=False,
          with_qualifiers=True,
          include_empty=True,
        )

        run_config = RunConfiguration([output_config])
        metadata = Metadata("test")
        parser = Csv()
        self.assertEqual("Csv", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        print(report.last_error)
        self.assertEqual(None, report.last_error)

        expected_lines = 22
        lines = report.output_reports[0].file_reports[0].num_lines
        self.assertEqual(lines, expected_lines)

        filename = report.output_reports[0].file_reports[0].file_name

        self.assertEqual(filename, output_file)

        with open(output_file) as fp:
            i = 0
            for line in fp:
                js = json.loads(line)
                if i == 21:
                    self.assertEqual(
                        js["name"],
                        "PSEXESVC",
                    )
                    self.assertEqual(
                        js["executable_path"],
                        "C:\\WINDOWS\\PSEXESVC.exe",
                    )
                i += 1
            self.assertEqual(i, expected_lines)
