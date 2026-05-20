import json
import os
from unittest import TestCase

from dfir_ogre_common import Metadata, OutputConfiguration, RunConfiguration

from dfir_ogre_plugin_windows import RegExp

from . import BASE_TEMP_FOLDER, CONF_FOLDER

DATA_FOLDER = os.path.join("tests", "data")
TEMP_FOLDER = os.path.join(BASE_TEMP_FOLDER, "pca")
os.makedirs(TEMP_FOLDER, exist_ok=True)


class TestPca(TestCase):
    # python -m unittest tests.test_pca.TestPca.test_general_db0 -v
    def test_general_db0(self):
        plugin_file = os.path.join(CONF_FOLDER, "pca_general_record.xml")
        input_file = os.path.join(DATA_FOLDER, "pca", "PcaGeneralDb0.txt")

        base_output_name = "pca_general_0"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".pca_general_record.jsonl"
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
        parser = RegExp()
        self.assertEqual("Regexp", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 51
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
                        "executable_path: %programfiles%\\freefilesync\\freefilesync.exe",
                    )
                    self.assertEqual(
                        js["additional_description"],
                        "file_description: freefilesync",
                    )

                i += 1
            self.assertEqual(i, expected_lines)

    # python -m unittest tests.test_pca.TestPca.test_general_db1 -v
    def test_general_db1(self):
        plugin_file = os.path.join(CONF_FOLDER, "pca_general_record.xml")
        input_file = os.path.join(DATA_FOLDER, "pca", "PcaGeneralDb1.txt")

        base_output_name = "pca_general_1"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".pca_general_record.jsonl"
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

        configuration = RunConfiguration([output_config])
        metadata = Metadata("test")
        parser = RegExp()
        self.assertEqual("Regexp", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, configuration, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 125
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
                        "executable_path: %programfiles%\\freefilesync\\freefilesync.exe",
                    )
                    self.assertEqual(
                        js["additional_description"],
                        "file_description: freefilesync",
                    )

                i += 1
            self.assertEqual(i, expected_lines)

    # python -m unittest tests.test_pca.TestPca.test_general_db2 -v
    def test_general_db2(self):
        plugin_file = os.path.join(CONF_FOLDER, "pca_general_record.xml")
        input_file = os.path.join(DATA_FOLDER, "pca", "PcaGeneralDb2.txt")

        base_output_name = "pca_general_2"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".pca_general_record.jsonl"
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
        parser = RegExp()
        self.assertEqual("Regexp", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 3
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
                        "executable_path: %programfiles%\\windowsapps\\microsoft.windowsterminal_1.12.10983.0_x64__8wekyb3d8bbwe\\wt.exe",
                    )
                    self.assertEqual(
                        js["additional_description"],
                        "file_description: windows terminal",
                    )

                i += 1
            self.assertEqual(i, expected_lines)

    # python -m unittest tests.test_pca.TestPca.test_app_launch0 -v
    def test_app_launch0(self):
        plugin_file = os.path.join(CONF_FOLDER, "pca_app_launch.xml")
        input_file = os.path.join(DATA_FOLDER, "pca", "PcaAppLaunchDic0.txt")

        base_output_name = "pca_app_launch_0"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".pca_app_launch.jsonl"
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
        parser = RegExp()
        self.assertEqual("Regexp", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        print(report.last_error)
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
                if i == 0:
                    self.assertEqual(
                        js["description"],
                        "executable_path: C:\\Program Files\\WindowsApps\\MicrosoftTeams_22248.701.1548.6610_x64__8wekyb3d8bbwe\\msteams.exe",
                    )

                i += 1
            self.assertEqual(i, expected_lines)

    # python -m unittest tests.test_pca.TestPca.test_app_launch1 -v
    def test_app_launch1(self):
        plugin_file = os.path.join(CONF_FOLDER, "pca_app_launch.xml")
        input_file = os.path.join(DATA_FOLDER, "pca", "PcaAppLaunchDic1.txt")

        base_output_name = "pca_app_launch_1"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".pca_app_launch.jsonl"
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
        parser = RegExp()
        self.assertEqual("Regexp", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        print(report.last_error)
        self.assertEqual(None, report.last_error)

        expected_lines = 55
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
                        "executable_path: C:\\ProgramData\\Sophos\\AutoUpdate\\Cache\\sophos_autoupdate1.dir\\su-setup32.exe",
                    )

                i += 1
            self.assertEqual(i, expected_lines)
