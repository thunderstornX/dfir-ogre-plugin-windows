import logging
from typing import List

from construct import Bytes, GreedyRange, Int32ul, Struct, this
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from dfir_ogre_common import (
    Metadata,
    OgrePlugin,
    Output,
    PluginConfiguration,
    PluginDescription,
    Record,
    Registry,
    RegKey,
    RunConfiguration,
    RunReport,
    Value,
)

from dfir_ogre_plugin_windows.common import value

logger = logging.getLogger(__name__)


class RegSystemCertificates(OgrePlugin):
    def description(self) -> PluginDescription:
        return PluginDescription(
            "RegSystemCertificates",
            "Get system wide X509 certificates from Software hive",
        )

    def parse(
        self,
        input_file: str,
        plugin_file: str,
        run_config: RunConfiguration,
        metadata: Metadata,
    ) -> RunReport:
        plugin_config = PluginConfiguration.load(plugin_file)
        report = RunReport()
        try:
            reg = Registry.load(input_file, "\\HKLM\\Software")
        except Exception as e:
            report.add_error(f"{e}")
            return report

        paths = [
            "\\HKLM\\Software\\Microsoft\\SystemCertificates\\*\\Certificates\\*",
            "\\HKLM\\Software\\Microsoft\\EnterpriseCertificates\\*\\Certificates\\*",
            "\\HKLM\\Software\\Policies\\Microsoft\\SystemCertificates\\*\\Certificates\\*",
        ]

        with Output(run_config, plugin_config, metadata) as output:
            parse_path(reg, paths, output, report)

            report.add_output_report(output.get_report())

        return report


class RegUserCertificates(OgrePlugin):
    def description(self) -> PluginDescription:
        return PluginDescription(
            "RegUserCertificates",
            "(no test data) Get X509 certificates from NTUser.dat hive",
        )

    def parse(
        self,
        input_file: str,
        plugin_file: str,
        run_config: RunConfiguration,
        metadata: Metadata,
    ) -> RunReport:
        plugin_config = PluginConfiguration.load(plugin_file)
        report = RunReport()
        try:
            reg = Registry.load(input_file, "\\HKCU")
        except Exception as e:
            report.add_error(f"{e}")
            return report

        paths = [
            "\\HKCU\\Software\\Microsoft\\SystemCertificates\\*\\Certificates\\*",
            "\\HKCU\\Software\\Microsoft\\EnterpriseCertificates\\*\\Certificates\\*",
            "\\HKCU\\Software\\Policies\\Microsoft\\SystemCertificates\\*\\Certificates\\*",
        ]

        with Output(run_config, plugin_config, metadata) as output:
            parse_path(reg, paths, output, report)

            report.add_output_report(output.get_report())

        return report


def parse_path(reg: Registry, paths: List[str], output: Output, report: RunReport):
    for path in paths:
        try:
            keys = reg.glob_keys(path)
            for key in keys:
                parse_key(key, output, report)
        except Exception as e:
            report.add_error(f"{e}")


def parse_key(key: RegKey, output: Output, report: RunReport):
    try:
        cert_blob = key.value_data("Blob")
        if isinstance(cert_blob, bytes):
            # cert_blob = cert_blob.copy()
            BLOB_CERTIF_STRUCT = Struct(
                "elements"
                / GreedyRange(
                    Struct(
                        "type" / Int32ul,
                        "count" / Int32ul,
                        "size" / Int32ul,                          "cert_der" / Bytes(this.size * this.count),
                    )
                )
            )
            certificates = BLOB_CERTIF_STRUCT.parse(cert_blob)

            for element in certificates.elements:
                try:
                    cert = x509.load_der_x509_certificate(element.cert_der)
                except Exception as e:
                    logger.debug(
                        f"parsing_error: {e} for der: 0x{bytes(element.cert_der).hex()}"
                    )
                    continue

                tuple = Record()

                tuple.add("subject", Value.String(cert.subject.rfc4514_string()))

                tuple.add("issuer", Value.String(cert.issuer.rfc4514_string()))

                tuple.add(
                    "not_valid_before",
                    Value.Date(cert.not_valid_before_utc),
                )

                tuple.add(
                    "not_valid_after",
                    Value.Date(cert.not_valid_after_utc),
                )

                tuple.add(
                    "pub_key_algo",
                    Value.String(cert.public_key_algorithm_oid._name),
                )
                tuple.add(
                    "pub_key_algo_oid",
                    Value.String(cert.public_key_algorithm_oid.dotted_string),
                )

                tuple.add(
                    "fingerprint_sha256",
                    Value.String(cert.fingerprint(hashes.SHA256()).hex()),
                )

                tuple.add("version", Value.String(str(cert.version)))

                serial_number = cert.serial_number
                tuple.add("serial_number", Value.String(str(serial_number)))

                extensions = []
                for extension in cert.extensions:
                    ext_tuple = Record()
                    extension: x509.Extension[x509.ExtensionType] = extension
                    ext_tuple.add("name", Value.String(str(extension.oid._name)))
                    ext_tuple.add("oid", Value.String(str(extension.oid.dotted_string)))
                    ext_tuple.add("critical", Value.Bool(extension.critical))
                    ext_tuple.add("value", Value.String(str(extension.value)))
                    extensions.append(Value.Object(ext_tuple))

                tuple.add("extensions", Value.Array(extensions))

                tuple.add(
                    "subject_bytes",
                    Value.String(f"0x{cert.subject.public_bytes().hex()}"),
                )

                tuple.add(
                    "issuer_bytes",
                    Value.String(f"0x{cert.issuer.public_bytes().hex()}"),
                )
                tuple.add("key_path", value(key.path))
                tuple.add("key_modif_time", value(key.mtime))
                tuple.add(
                    "key_security", Value.Object(key.security_descriptor.to_record())
                )
                tuple.add("der", Value.String(f"0x{bytes(element.cert_der).hex()}"))
                output.write(tuple)
    except Exception as e:
        logger.error(f"{e}")
        report.add_error(f"{e}")
