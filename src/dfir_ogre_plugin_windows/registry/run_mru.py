import logging
import string

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

# from .api import RegKey, Registry
from dfir_ogre_plugin_windows.common import value

logger = logging.getLogger(__name__)


class RegRunMru(OgrePlugin):
    def description(self) -> PluginDescription:
        return PluginDescription(
            "RegRunMru",
            "Get 'Run' (WINDOWS+R) commands from NTUser hive",
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

        with Output(run_config, plugin_config, metadata) as output:
            try:
                keys = reg.glob_keys(
                    "\\HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU"
                )
                for key in keys:
                    self.parse_key(key, output, report)
            except Exception as e:
                report.add_error(f"{e}")

            report.add_output_report(output.get_report())

        return report

    def parse_key(self, key: RegKey, output: Output, report: RunReport):
        try:
            for key_val in key.values():
                ascii_lower_chars = list(string.ascii_lowercase)
                val_name = key_val.name()
                if val_name in ascii_lower_chars:
                    tuple = Record()
                    tuple.add("executable", value(key_val.data()))
                    tuple.add("index", value(val_name))
                    tuple.add("key_path", value(key.path))
                    tuple.add("key_modif_time", value(key.mtime))
                    tuple.add(
                        "key_security",
                        Value.Object(key.security_descriptor.to_record()),
                    )
                    output.write(tuple)

        except Exception as e:
            report.add_error(f"{e}")
