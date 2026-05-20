import json
import os
from unittest import TestCase

from dfir_ogre_common import Metadata, OutputConfiguration, RunConfiguration

from dfir_ogre_plugin_windows import Prefetch

from . import BASE_TEMP_FOLDER, CONF_FOLDER

DATA_FOLDER = os.path.join("tests", "data")
TEMP_FOLDER = os.path.join(BASE_TEMP_FOLDER, "prefetch")
os.makedirs(TEMP_FOLDER, exist_ok=True)


class TestPrefetch(TestCase):
    # python -m unittest tests.test_prefetch.TestPrefetch.test_prefetch_w7 -v
    def test_prefetch_w7(self):
        plugin_file = os.path.join(CONF_FOLDER, "prefetch.xml")
        input_file = os.path.join(
            DATA_FOLDER, "prefetch", "W7", "AUTORUNSC.EXE-B8F1A907.pf"
        )

        base_output_name = "prefetch_w7"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".prefetch.jsonl"
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
        parser = Prefetch()
        self.assertEqual("Prefetch", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 2
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
                        "executable: AUTORUNSC.EXE",
                    )
                    self.assertEqual(
                        js["additional_description"],
                        "path_hints: [\\WINDOWS\\TEMP\\WORKINGTEMP\\AUTORUNSC.EXE]",
                    )

                i += 1
            self.assertEqual(i, expected_lines)

    # python -m unittest tests.test_prefetch.TestPrefetch.test_prefetch_w8_autoruns -v
    def test_prefetch_w8_autoruns(self):
        plugin_file = os.path.join(CONF_FOLDER, "prefetch.xml")
        input_file = os.path.join(
            DATA_FOLDER, "prefetch", "W81", "AUTORUNSC.EXE-74270A5A.pf"
        )

        base_output_name = "prefetch_w8_autoruns"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".prefetch.jsonl"
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
        parser = Prefetch()
        self.assertEqual("Prefetch", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 2
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
                        "executable: AUTORUNSC.EXE",
                    )
                    self.assertEqual(
                        js["additional_description"],
                        "path_hints: [\\WINDOWS\\TEMP\\AUTORUNSC.EXE]",
                    )

                i += 1
            self.assertEqual(i, expected_lines)

    # python -m unittest tests.test_prefetch.TestPrefetch.test_prefetch_w8_cmd -v
    def test_prefetch_w8_cmd(self):
        plugin_file = os.path.join(CONF_FOLDER, "prefetch.xml")
        input_file = os.path.join(DATA_FOLDER, "prefetch", "W81", "CMD.EXE-CD245F9E.pf")

        base_output_name = "prefetch_w8_cmd"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".prefetch.jsonl"
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
        parser = Prefetch()
        self.assertEqual("Prefetch", parser.description().command)  # type: ignore

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
                if i == 0:
                    self.assertEqual(
                        js["description"],
                        "executable: CMD.EXE",
                    )
                    self.assertEqual(
                        js["additional_description"],
                        "path_hints: [\\WINDOWS\\SYSTEM32\\CMD.EXE]",
                    )

                i += 1
            self.assertEqual(i, expected_lines)

    # python -m unittest tests.test_prefetch.TestPrefetch.test_prefetch_w10_autoruns -v
    def test_prefetch_w10_autoruns(self):
        plugin_file = os.path.join(CONF_FOLDER, "prefetch.xml")
        input_file = os.path.join(
            DATA_FOLDER, "prefetch", "W10-22H2", "AUTORUNSC.EXE-C047C10D.pf"
        )

        base_output_name = "prefetch_w10_autoruns"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".prefetch.jsonl"
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
        parser = Prefetch()
        self.assertEqual("Prefetch", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 2
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
                        "executable: AUTORUNSC.EXE",
                    )
                    self.assertEqual(
                        js["additional_description"],
                        "path_hints: [\\WINDOWS\\TEMP\\AUTORUNSC.EXE]",
                    )

                i += 1
            self.assertEqual(i, expected_lines)

    # python -m unittest tests.test_prefetch.TestPrefetch.test_prefetch_w10_cmd -v
    def test_prefetch_w10_cmd(self):
        plugin_file = os.path.join(CONF_FOLDER, "prefetch.xml")
        input_file = os.path.join(
            DATA_FOLDER, "prefetch", "W10-22H2", "CMD.EXE-6D6290C5.pf"
        )

        base_output_name = "prefetch_w10_cmd"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".prefetch.jsonl"
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
        parser = Prefetch()
        self.assertEqual("Prefetch", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 10
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
                        "executable: CMD.EXE",
                    )
                    self.assertEqual(
                        js["additional_description"],
                        "path_hints: [\\WINDOWS\\SYSWOW64\\CMD.EXE]",
                    )

                i += 1
            self.assertEqual(i, expected_lines)

    # python -m unittest tests.test_prefetch.TestPrefetch.test_prefetch_w10_orc -v
    def test_prefetch_w10_orc(self):
        plugin_file = os.path.join(CONF_FOLDER, "prefetch.xml")
        input_file = os.path.join(
            DATA_FOLDER, "prefetch", "W10-22H2", "ORC_PTF2REF_10.1.7.EXE-BA772821.pf"
        )

        base_output_name = "prefetch_w10_orc"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".prefetch.jsonl"
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
        parser = Prefetch()
        self.assertEqual("Prefetch", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 2
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
                        "executable: ORC_PTF2REF_10.1.7.EXE",
                    )
                    self.assertEqual(
                        js["additional_description"],
                        "path_hints: []",
                    )

                i += 1
            self.assertEqual(i, expected_lines)

    # python -m unittest tests.test_prefetch.TestPrefetch.test_prefetch_w10_dll -v
    def test_prefetch_w10_dll(self):
        plugin_file = os.path.join(CONF_FOLDER, "prefetch.xml")
        input_file = os.path.join(
            DATA_FOLDER, "prefetch", "W10-22H2", "RUNDLL32.EXE-20A3C999.pf"
        )

        base_output_name = "prefetch_w10_dll"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".prefetch.jsonl"
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
        parser = Prefetch()
        self.assertEqual("Prefetch", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 4
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
                        "executable: RUNDLL32.EXE",
                    )
                    self.assertEqual(
                        js["additional_description"],
                        "path_hints: [\\WINDOWS\\SYSTEM32\\RUNDLL32.EXE]",
                    )

                i += 1
            self.assertEqual(i, expected_lines)
