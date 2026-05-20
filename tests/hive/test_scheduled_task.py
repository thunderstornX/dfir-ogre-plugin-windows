import json
import os
from unittest import TestCase

from dfir_ogre_common import Metadata, OutputConfiguration, RunConfiguration

from dfir_ogre_plugin_windows import RegScheduledTask

from . import CONF_FOLDER, DATA_FOLDER, TEMP_FOLDER

os.makedirs(TEMP_FOLDER, exist_ok=True)


class TestScheduledTask(TestCase):
    # python -m unittest tests.hive.test_scheduled_task.TestScheduledTask.test_scheduled_task -v
    def test_scheduled_task(self):
        plugin_file = os.path.join(CONF_FOLDER, "scheduled_task.xml")
        input_file = os.path.join(DATA_FOLDER, "hive", "SOFTWARE.dat")

        base_output_name = "scheduled_task"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".scheduled_tasks.jsonl"
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

        metadata = Metadata("test")
        parser = RegScheduledTask()
        self.assertEqual("RegScheduledTask", parser.description().command)  # type: ignore

        run_config = RunConfiguration([output_config])
        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 530
        lines = report.output_reports[0].file_reports[0].num_lines
        self.assertEqual(lines, expected_lines)

        filename = report.output_reports[0].file_reports[0].file_name
        self.assertEqual(filename, output_file)

        with open(output_file) as fp:
            i = 0
            for line in fp:
                jsoned = json.loads(line)

                if i == 14:
                    self.assertEqual(jsoned["related_user"], "S-1-5-32-544")
                    self.assertEqual(
                        jsoned["description"],
                        "task: \\Microsoft\\Windows\\UPnP\\UPnPHostConfig",
                    )
                    self.assertEqual(
                        jsoned["additional_description"],
                        "action_type: Exec - exec_command: sc.exe - exec_arguments: config upnphost start= auto",
                    )
                    data = jsoned["data"]
                    self.assertEqual(
                        data["creation_date:creation_date"],
                        "2016-01-21T18:20:43.399251+00:00",
                    )
                    self.assertEqual(
                        data["plain"]["mtime:modification_date"],
                        "2015-10-30T07:25:55.704575+00:00",
                    )

                i += 1
            # self.assertEqual(i, expected_lines)
