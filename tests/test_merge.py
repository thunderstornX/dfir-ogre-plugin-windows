import json
import os
from unittest import TestCase

from dfir_ogre_common import Metadata, OutputConfiguration, RunConfiguration

from dfir_ogre_plugin_windows import MergeLine

from . import BASE_TEMP_FOLDER, CONF_FOLDER

DATA_FOLDER = os.path.join("tests", "data")
TEMP_FOLDER = os.path.join(BASE_TEMP_FOLDER, "merge")
os.makedirs(TEMP_FOLDER, exist_ok=True)


class MergeTest(TestCase):
    #  python -m unittest tests.test_merge.MergeTest.test_merge -v
    def test_merge(self):
        plugin_file = os.path.join(CONF_FOLDER, "merge_file.xml")
        input_file = os.path.join(DATA_FOLDER, "merge", "hello.txt")
        base_output_name = "merge_hello"

        output_file = os.path.join(TEMP_FOLDER, base_output_name + ".merge_file.jsonl")
        if os.path.exists(output_file):
            os.remove(output_file)

        output_config = OutputConfiguration(
          base_output_name,
          TEMP_FOLDER,
          with_timeline=False,
                    include_empty=True,
        )

        run_config = RunConfiguration([output_config])

        metadata = Metadata("test")
        parser = MergeLine()
        self.assertEqual("Merge", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        lines = report.output_reports[0].file_reports[0].num_lines

        self.assertEqual(lines, 1)

        filename = report.output_reports[0].file_reports[0].file_name

        self.assertEqual(filename, output_file)

        with open(output_file) as fp:
            i = 0
            for line in fp:
                jsoned = json.loads(line)
                self.assertEqual(jsoned["data"], "Hello\nWorld\n!")
                i += 1
            self.assertEqual(i, 1)
