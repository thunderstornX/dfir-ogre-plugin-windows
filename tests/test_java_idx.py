import json
import os
from unittest import TestCase

from dfir_ogre_common import Metadata, OutputConfiguration, RunConfiguration

from dfir_ogre_plugin_windows import JavaIdx

from . import BASE_TEMP_FOLDER, CONF_FOLDER

DATA_FOLDER = os.path.join("tests", "data")
TEMP_FOLDER = os.path.join(BASE_TEMP_FOLDER, "java_idx")
os.makedirs(TEMP_FOLDER, exist_ok=True)


class TestJavaIdx(TestCase):
    # python -m unittest tests.test_java_idx.TestJavaIdx.test_idx_602 -v
    def test_idx_602(self):
        plugin_file = os.path.join(CONF_FOLDER, "java_idx.xml")

        input_file = os.path.join(DATA_FOLDER, "java_idx", "java_602.idx")

        base_output_name = "java_idx_602"

        output_file = os.path.join(TEMP_FOLDER, base_output_name + ".java_idx.jsonl")
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
        parser = JavaIdx()
        self.assertEqual("JavaIdx", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, configuration, metadata)
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
                        "url: http://www.gxxxxx.com/a/java/xxz.jar",
                    )
                    self.assertEqual(
                        js["additional_description"],
                        "content_length: 14180 - is_shortcut: false",
                    )

                i += 1
            self.assertEqual(i, expected_lines)

    # python -m unittest tests.test_java_idx.TestJavaIdx.test_idx -v
    def test_idx(self):
        plugin_file = os.path.join(CONF_FOLDER, "java_idx.xml")
        input_file = os.path.join(DATA_FOLDER, "java_idx", "java.idx")

        base_output_name = "java_idx"

        output_file = os.path.join(TEMP_FOLDER, base_output_name + ".java_idx.jsonl")
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
        parser = JavaIdx()
        self.assertEqual("JavaIdx", parser.description().command)  # type: ignore

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
                        "url: http://xxxxc146d3.gxhjxxwsf.xx:82/forum/dare.php?hsh=6&key=b30xxxx1c597xxxx15d593d3f0xxx1ab - ip_address: 10.7.119.10",
                    )
                    self.assertEqual(
                        js["additional_description"],
                        "content_length: 7162 - is_shortcut: false - signed: false",
                    )

                i += 1
            self.assertEqual(i, expected_lines)
