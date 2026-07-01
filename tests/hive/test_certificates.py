import json
import os
from unittest import TestCase

from dfir_ogre_common import Metadata, OutputConfiguration, RunConfiguration

from src.dfir_ogre_plugin_windows import RegSystemCertificates, RegUserCertificates

from . import CONF_FOLDER, TEMP_FOLDER

DATA_FOLDER = os.path.join("tests", "data")
os.makedirs(TEMP_FOLDER, exist_ok=True)


class Certificates(TestCase):
    # python -m unittest tests.hive.test_certificates.Certificates.test_system_certificate -v
    def test_system_certificate(self):
        plugin_file = os.path.join(CONF_FOLDER, "certificates_software.xml")
        input_file = os.path.join(DATA_FOLDER, "hive", "SOFTWARE.dat")

        base_output_name = "certificates_system"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".x509_cert.jsonl"
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
        parser = RegSystemCertificates()
        self.assertEqual("RegSystemCertificates", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 84
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
                        "subject: CN=AddTrust External CA Root,OU=AddTrust External TTP Network,O=AddTrust AB,C=SE",
                    )
                    self.assertEqual(
                        js["additional_description"],
                        "issuer: CN=AddTrust External CA Root,OU=AddTrust External TTP Network,O=AddTrust AB,C=SE",
                    )

                i += 1
            self.assertEqual(i, expected_lines)

    def test_user_certificate(self):
        plugin_file = os.path.join(CONF_FOLDER, "certificates_users.xml")

        input_file = os.path.join(DATA_FOLDER, "hive", "NTUSER.dat")

        base_output_name = "certificates_user"

        output_file = os.path.join(
            TEMP_FOLDER, base_output_name + ".x509_cert.jsonl"
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
        parser = RegUserCertificates()
        self.assertEqual("RegUserCertificates", parser.description().command)  # type: ignore

        report = parser.parse(input_file, plugin_file, run_config, metadata)
        self.assertEqual(None, report.last_error)

        expected_lines = 0
        lines = report.output_reports[0].file_reports[0].num_lines
        self.assertEqual(lines, expected_lines)

        filename = report.output_reports[0].file_reports[0].file_name
        self.assertEqual(filename, output_file)

        # with open(output_file) as fp:
        #     i = 0
        #     for line in fp:
        #         js = json.loads(line)
        #         if i == 0:
        #             self.assertEqual(
        #                 js["description"],
        #                 "subject: CN=AddTrust External CA Root,OU=AddTrust External TTP Network,O=AddTrust AB,C=SE",
        #             )
        #             self.assertEqual(
        #                 js["additional_description"],
        #                 "issuer: CN=AddTrust External CA Root,OU=AddTrust External TTP Network,O=AddTrust AB,C=SE",
        #             )

        #         i += 1
        #     self.assertEqual(i, expected_lines)
