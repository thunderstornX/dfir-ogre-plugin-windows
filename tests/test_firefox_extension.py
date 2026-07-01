import json
import os
from unittest import TestCase

from dfir_ogre_common import Metadata, OutputConfiguration, RunConfiguration

from dfir_ogre_plugin_windows import FirefoxExtension

from . import BASE_TEMP_FOLDER, CONF_FOLDER

DATA_FOLDER = os.path.join("tests", "data")
TEMP_FOLDER = os.path.join(BASE_TEMP_FOLDER, "browser_extension")
os.makedirs(TEMP_FOLDER, exist_ok=True)


class TestFirefoxExtension(TestCase):
    # python -m unittest tests.test_firefox_extension.TestFirefoxExtension.test_firefox -v
    def test_firefox(self):
        plugin_file = os.path.join(CONF_FOLDER, "firefox_extension.xml")
        input_file = os.path.join(
            DATA_FOLDER, "browser_extension", "firefox_extensions.json"
        )

        base_output_name = "firefox"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".firefox_extension.jsonl"
        )
        if os.path.exists(output_file):
            os.remove(output_file)

        output_config = OutputConfiguration(
          base_output_name,
          TEMP_FOLDER,
          with_timeline=True,
                    include_empty=False,
        )

        metadata = Metadata("test")
        parser = FirefoxExtension()
        self.assertEqual("FirefoxExtension", parser.description().command)  # type: ignore

        run_config = RunConfiguration([output_config])
        report = parser.parse(input_file, plugin_file, run_config, metadata)
        # Some builtin data don't not have dates
        self.assertEqual(
            None, report.last_error
        )

        expected_lines = 12
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
                        "name: Dictionnaire français - browser: firefox",
                    )
                    self.assertEqual(
                        js["additional_description"],
                        "description: Dictionnaire orthographique pour la langue française. - path: /home/asalais/snap/firefox/common/.mozilla/firefox/9j2syrh4.default-release/extensions/fr-dicollecte@dictionaries.addons.mozilla.org.xpi",
                    )
                if i == 11:
                    self.assertEqual(
                        js["description"],
                        "name: Dark Reader - browser: firefox",
                    )
                    self.assertEqual(
                        js["additional_description"],
                        "description: Dark mode for every website. Take care of your eyes, use dark theme for night and daily browsing. - path: /home/asalais/snap/firefox/common/.mozilla/firefox/9j2syrh4.default-release/extensions/addon@darkreader.org.xpi - source_uri: https://addons.mozilla.org/firefox/downloads/file/4598977/darkreader-4.9.112.xpi",
                    )

                i += 1
            self.assertEqual(i, expected_lines)
