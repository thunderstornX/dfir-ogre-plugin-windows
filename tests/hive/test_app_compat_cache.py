import json
import os
from unittest import TestCase

from dfir_ogre_common import Metadata, OutputConfiguration, RunConfiguration

from dfir_ogre_plugin_windows import RegAppCompatCache

from . import CONF_FOLDER, TEMP_FOLDER

DATA_FOLDER = os.path.join("tests", "data")


class AppCompatCache(TestCase):
    # python -m unittest tests.hive.test_app_compat_cache.AppCompatCache.test_compat_cache -v
    def test_compat_cache(self):
        plugin_file = os.path.join(CONF_FOLDER, "app_compat_cache.xml")

        input_file = os.path.join(DATA_FOLDER, "hive", "SYSTEM.dat")
        base_output_name = "app_compat_cache"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".app_compat_cache.jsonl"
        )
        if os.path.exists(output_file):
            os.remove(output_file)

        output_config = OutputConfiguration(
          base_output_name,
          TEMP_FOLDER,
          with_timeline=True,
                    include_empty=True,
        )
        run_config = RunConfiguration([output_config])

        metadata = Metadata("test")
        parser = RegAppCompatCache()
        self.assertEqual("RegAppCompatCache", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 108
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
                        js["related_user"],
                        "S-1-5-18",
                    )

                    self.assertEqual(
                        js["description"],
                        "path: C:\\WINDOWS\\system32\\ie4ushowIE.exe",
                    )

                i += 1
            self.assertEqual(i, expected_lines)

    # python -m unittest tests.hive.test_app_compat_cache.AppCompatCache.test_compat_cache_2 -v
    def test_compat_cache_2(self):
        plugin_file = os.path.join(CONF_FOLDER, "app_compat_cache.xml")

        input_file = os.path.join(DATA_FOLDER, "hive", "SYSTEM_2.dat")

        base_output_name = "app_compat_cache_2"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".app_compat_cache.jsonl"
        )
        if os.path.exists(output_file):
            os.remove(output_file)

        output_config = OutputConfiguration(
          base_output_name,
          TEMP_FOLDER,
          with_timeline=True,
                    include_empty=True,
        )
        run_config = RunConfiguration([output_config])
        metadata = Metadata("test")
        parser = RegAppCompatCache()
        self.assertEqual("RegAppCompatCache", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 474
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
                        js["related_user"],
                        "S-1-5-18",
                    )

                    self.assertEqual(
                        js["description"],
                        "path: C:\\Windows\\SysWOW64\\cmd.exe",
                    )

                i += 1
            self.assertEqual(i, expected_lines)
