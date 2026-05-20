import logging
import uuid

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


class RegSIPP(OgrePlugin):
    def description(self) -> PluginDescription:
        return PluginDescription(
            "RegSIPP",
            "List Subject Interface Package from Software Hive",
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
            reg = Registry.load(input_file, "\\HKLM\\SOFTWARE")
        except Exception as e:
            report.add_error(f"{e}")
            return report

        with Output(run_config, plugin_config, metadata) as output:
            try:
                keys = reg.glob_keys(
                    "\\HKLM\\SOFTWARE\\Microsoft\\Cryptography\\OID\\EncodingType 0\\CryptSIPDllVerifyIndirectData\\*"
                )
                for key in keys:
                    self.parse_key(key, output, report)
            except Exception as e:
                report.add_error(f"{e}")

            report.add_output_report(output.get_report())

        return report

    def parse_key(self, key: RegKey, output: Output, report: RunReport):
        try:
            tuple = Record()
            sip_guid = uuid.UUID(key.name)
            tuple.add("guid", value(str(sip_guid)))

            guid_name = SIP_NAMES.get(sip_guid, None)
            tuple.add("name", value(guid_name))

            dll = key.value_data("Dll")
            tuple.add("dll", value(dll))

            function_name = key.value_data("FuncName")
            tuple.add("function_name", value(function_name))

            tuple.add("key_path", value(key.path))
            tuple.add("key_modif_time", value(key.mtime))
            tuple.add("key_security", Value.Object(key.security_descriptor.to_record()))
            output.write(tuple)
        except Exception as e:
            report.add_error(f"{e}")


SIP_NAMES = {
    uuid.UUID("000C10F1-0000-0000-C000-000000000046"): "MSIP",
    uuid.UUID("06C9E010-38CE-11D4-A2A3-00104BD35090"): "WSHJScript",
    uuid.UUID("0AC5DF4B-CE07-4DE2-B76E-23C839A09FD1"): "AppX",
    uuid.UUID("0F5F58B3-AADE-4B9A-A434-95742D92ECEB"): "AppXBundle",
    uuid.UUID("1629F04E-2799-4DB5-8FE5-ACE10F17EBAB"): "WSHVBScript",
    uuid.UUID("1A610570-38CE-11D4-A2A3-00104BD35090"): "WSHWindowsScriptFile",
    uuid.UUID("5598CFF1-68DB-4340-B57F-1CACF88C9A51"): "AppXP7XSignature",
    uuid.UUID("603BCC1F-4B59-4E08-B724-D2C6297EF351"): "PowerShell",
    uuid.UUID("9BA61D3F-E73A-11D0-8CD2-00C04FC295EE"): "CTL",
    uuid.UUID("9F3053C5-439D-4BF7-8A77-04F0450A1D9F"): "ElectronicSoftwareDistribution",
    uuid.UUID("9FA65764-C36F-4319-9737-658A34585BB7"): "MicrosoftOfficeVBA",
    uuid.UUID("C689AAB8-8E78-11D0-8C47-00C04FC295EE"): "PortableExecutable",
    uuid.UUID("C689AAB9-8E78-11D0-8C47-00C04FC295EE"): "JavaClass",
    uuid.UUID("C689AABA-8E78-11D0-8C47-00C04FC295EE"): "Cabinet",
    uuid.UUID("CF78C6DE-64A2-4799-B506-89ADFF5D16D6"): "AppXEncrypted",
    uuid.UUID("D1D04F0C-9ABA-430D-B0E4-D7E96ACCE66C"): "AppXEncryptedBundle",
    uuid.UUID("DE351A42-8E59-11D0-8C47-00C04FC295EE"): "Flat",
    uuid.UUID("DE351A43-8E59-11D0-8C47-00C04FC295EE"): "Catalog",
}
