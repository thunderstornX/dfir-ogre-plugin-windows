import json
import os
from unittest import TestCase

from dfir_ogre_common import Metadata, OutputConfiguration, RunConfiguration

from dfir_ogre_plugin_windows import ChromeExtension

from . import BASE_TEMP_FOLDER

DATA_FOLDER = os.path.join("tests", "data")
CONF_FOLDER = os.path.join("configuration")
TEMP_FOLDER = os.path.join(BASE_TEMP_FOLDER, "browser_extension")
os.makedirs(TEMP_FOLDER, exist_ok=True)


class TestChromeExtension(TestCase):
    # python -m unittest tests.test_chrome_extension.TestChromeExtension.test_chrome -v
    def test_chrome(self):
        plugin_file = os.path.join(CONF_FOLDER, "chrome_extension.xml")

        input_file = os.path.join(
            DATA_FOLDER, "browser_extension", "chrome_manifest.json"
        )

        base_output_name = "chrome"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".chrome_extension.jsonl"
        )
        if os.path.exists(output_file):
            os.remove(output_file)

        output_config = OutputConfiguration(
          base_output_name,
          TEMP_FOLDER,
          with_timeline=False,
                    include_empty=False,
        )

        metadata = Metadata("test")
        parser = ChromeExtension()
        self.assertEqual("ChromeExtension", parser.description().command)  # type: ignore

        run_config = RunConfiguration([output_config])
        report = parser.parse(input_file, plugin_file, run_config, metadata)
        # Some builtin data don't not have dates
        self.assertEqual(None, report.last_error)

        expected_lines = 1
        lines = report.output_reports[0].file_reports[0].num_lines
        self.assertEqual(lines, expected_lines)

        filename = report.output_reports[0].file_reports[0].file_name
        self.assertEqual(filename, output_file)

        with open(output_file) as fp:
            i = 0
            for line in fp:
                js = json.loads(line)

                self.assertEqual(js["name"], "Dark Reader")
                self.assertEqual(js["version"], "4.9.112")
                self.assertEqual(
                    js["update_url"], "https://clients2.google.com/service/update2/crx"
                )
                self.assertEqual(
                    js["permissions"],
                    ["alarms", "fontSettings", "scripting", "storage"],
                )
                self.assertEqual(js["optional_permissions"], ["contextMenus"])
                self.assertEqual(
                    js["extension_pages"],
                    "default-src 'none'; script-src 'self'; style-src 'self'; img-src * data:; connect-src *; navigate-to 'self' https://darkreader.org/* https://github.com/darkreader/darkreader/blob/main/CONTRIBUTING.md https://github.com/darkreader/darkreader https://twitter.com/darkreaderapp; media-src 'none'; child-src 'none'; worker-src 'none'; object-src 'none'",
                )
                i += 1
            self.assertEqual(i, expected_lines)
