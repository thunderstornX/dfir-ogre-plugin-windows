import json
import os
import dateutil.parser
from datetime import timezone

from unittest import TestCase

from dfir_ogre_common import Metadata, OutputConfiguration, RunConfiguration


from dfir_ogre_plugin_windows import Lnk

from . import BASE_TEMP_FOLDER, CONF_FOLDER

DATA_FOLDER = os.path.join("tests", "data")
TEMP_FOLDER = os.path.join(BASE_TEMP_FOLDER, "lnk")
os.makedirs(TEMP_FOLDER, exist_ok=True)


class TestLnk(TestCase):
    # python -m unittest tests.test_lnk.TestLnk.test_lnk -v
    def test_lnk(self):
        plugin_file = os.path.join(CONF_FOLDER, "lnk_batched.xml")
        input_file = os.path.join(DATA_FOLDER, "lnk", "desktop.lnk.data")
        base_output_name = "lnk_desktop"

        output_file = os.path.join(TEMP_FOLDER, base_output_name + ".lnk.jsonl")
        if os.path.exists(output_file):
            os.remove(output_file)

        output_config = OutputConfiguration(
          base_output_name,
          TEMP_FOLDER,
          with_timeline=True,
          include_empty=False,
        )

        run_config = RunConfiguration([output_config])
        metadata = Metadata("test")
        parser = Lnk()
        self.assertEqual("Lnk", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        lines = report.output_reports[0].file_reports[0].num_lines
        expected_tuples = 4
        self.assertEqual(lines, expected_tuples)

        filename = report.output_reports[0].file_reports[0].file_name

        self.assertEqual(filename, output_file)

        with open(output_file) as fp:
            i = 0
            for line in fp:
                js = json.loads(line)
                if i == 0:
                    self.assertEqual(
                        js["description"], "local_base_path: C:\\Users\\heznik\\Desktop"
                    )
                    # test lower case conversion
                    self.assertEqual(
                        js["data"]["header"]["guid"],
                        "00021401-0000-0000-c000-000000000046",
                    )

                    self.assertEqual(
                        js["data"]["extra"]["distributed_link_tracker"][
                            "droid_volume_identifier"
                        ],
                        "cb368e46-431e-4e6d-b3a9-7cbb6dd6a31f",
                    )

                    # test FRNHex python mapping
                    self.assertEqual(
                        js["data"]["extra"]["distributed_link_tracker"][
                            "droid_file_frn"
                        ],
                        "0x000000000000F5B0",
                    )

                    # test FRNSplit extension mapping
                    self.assertEqual(
                        js["data"]["extra"]["distributed_link_tracker"][
                            "birth_droid_file_record_number"
                        ],
                        62896,
                    )

                    # test FRNSplit extension mapping
                    self.assertEqual(
                        js["data"]["extra"]["distributed_link_tracker"][
                            "droid_file_record_number"
                        ],
                        62896,
                    )
                i += 1
            self.assertEqual(i, expected_tuples)

    # python -m unittest tests.test_lnk.TestLnk.test_lnk_metadata -v
    def test_lnk_metadata(self):
        plugin_file = os.path.join(CONF_FOLDER, "lnk_batched.xml")
        input_file = os.path.join(DATA_FOLDER, "lnk", "desktop.lnk.data")
        base_output_name = "lnk_desktop_with_date_metadata"

        output_file = os.path.join(TEMP_FOLDER, base_output_name + ".lnk.jsonl")
        if os.path.exists(output_file):
            os.remove(output_file)

        output_config = OutputConfiguration(
          base_output_name,
          TEMP_FOLDER,
          with_timeline=True,
                    include_empty=False,
        )

        run_config = RunConfiguration([output_config])
        metadata = Metadata("test")
        metadata.creation_date =   dateutil.parser.isoparse("2023-04-15T12:34:56Z").astimezone(
            timezone.utc
        )
        metadata.modif_date =   dateutil.parser.isoparse("2024-02-15T14:01:32Z").astimezone(
            timezone.utc
        )
        parser = Lnk()
        self.assertEqual("Lnk", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        lines = report.output_reports[0].file_reports[0].num_lines
        expected_tuples = 6
        self.assertEqual(lines, expected_tuples)

        filename = report.output_reports[0].file_reports[0].file_name

        self.assertEqual(filename, output_file)

        with open(output_file) as fp:
            i = 0
            for line in fp:
                js = json.loads(line)
                if i == 0:
                    self.assertEqual(
                        js["description"], "local_base_path: C:\\Users\\heznik\\Desktop"
                    )
                    # test lower case conversion
                    self.assertEqual(
                        js["data"]["header"]["guid"],
                        "00021401-0000-0000-c000-000000000046",
                    )

                    self.assertEqual(
                        js["data"]["extra"]["distributed_link_tracker"][
                            "droid_volume_identifier"
                        ],
                        "cb368e46-431e-4e6d-b3a9-7cbb6dd6a31f",
                    )

                    # test FRNHex
                    self.assertEqual(
                        js["data"]["extra"]["distributed_link_tracker"][
                            "droid_file_frn"
                        ],
                        "0x000000000000F5B0",
                    )

                    # test FRNSplit extension mapping
                    self.assertEqual(
                        js["data"]["extra"]["distributed_link_tracker"][
                            "birth_droid_file_record_number"
                        ],
                        62896,
                    )

                    # test FRNSplit extension mapping
                    self.assertEqual(
                        js["data"]["extra"]["distributed_link_tracker"][
                            "droid_file_record_number"
                        ],
                        62896,
                    )
                i += 1
            self.assertEqual(i, expected_tuples)

    # python -m unittest tests.test_lnk.TestLnk.test_lnk_include_empty -v
    def test_lnk_include_empty(self):
        plugin_file = os.path.join(CONF_FOLDER, "lnk_batched.xml")
        input_file = os.path.join(DATA_FOLDER, "lnk", "desktop.lnk.data")
        base_output_name = "lnk_include_empty"

        output_file = os.path.join(TEMP_FOLDER, base_output_name + ".lnk.jsonl")
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
        metadata.creation_date =   dateutil.parser.isoparse("2023-04-15T12:34:56Z").astimezone(
            timezone.utc
        )
        metadata.modif_date =   dateutil.parser.isoparse("2024-02-15T14:01:32Z").astimezone(
            timezone.utc
        )


        parser = Lnk()
        self.assertEqual("Lnk", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        lines = report.output_reports[0].file_reports[0].num_lines
        expected_tuples = 1
        self.assertEqual(lines, expected_tuples)

        filename = report.output_reports[0].file_reports[0].file_name

        self.assertEqual(filename, output_file)

        with open(output_file) as fp:
            i = 0
            for line in fp:
                js = json.loads(line)

                self.assertEqual(
                    "common_path_suffix" in js["link_info"],
                    True,
                )

                self.assertEqual(
                    js["link_info"]["location"],
                    "Local",
                )

                i += 1
            self.assertEqual(i, expected_tuples)

    # python -m unittest tests.test_lnk.TestLnk.test_lnk_remove_empty -v
    def test_lnk_remove_empty(self):
        plugin_file = os.path.join(CONF_FOLDER, "lnk_batched.xml")
        input_file = os.path.join(DATA_FOLDER, "lnk", "desktop.lnk.data")
        base_output_name = "lnk_remove_empty"

        output_file = os.path.join(TEMP_FOLDER, base_output_name + ".lnk.jsonl")
        if os.path.exists(output_file):
            os.remove(output_file)

        output_config = OutputConfiguration(
          base_output_name,
          TEMP_FOLDER,
          with_timeline=False,
          include_empty=False,
        )

        run_config = RunConfiguration([output_config])
        metadata = Metadata("test")
        metadata.creation_date =   dateutil.parser.isoparse("2023-04-15T12:34:56Z").astimezone(
            timezone.utc
        )
        metadata.modif_date =   dateutil.parser.isoparse("2024-02-15T14:01:32Z").astimezone(
            timezone.utc
        )

        parser = Lnk()
        self.assertEqual("Lnk", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        lines = report.output_reports[0].file_reports[0].num_lines
        expected_tuples = 1
        self.assertEqual(lines, expected_tuples)

        filename = report.output_reports[0].file_reports[0].file_name

        self.assertEqual(filename, output_file)

        with open(output_file) as fp:
            i = 0
            for line in fp:
                js = json.loads(line)

                self.assertEqual(
                    "common_path_suffix" in js["link_info"],
                    False,
                )

                self.assertEqual(
                    js["link_info"]["location"],
                    "Local",
                )

                i += 1
            self.assertEqual(i, expected_tuples)
