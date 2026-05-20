import logging

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


class RegPendingRename(OgrePlugin):
    def description(self) -> PluginDescription:
        return PluginDescription(
            "RegPendingRename",
            "List pending file rename operations that will take place at next reboot, from System hive",
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
            reg = Registry.load(input_file, "\\HKLM\\System")
        except Exception as e:
            report.add_error(f"{e}")
            return report

        with Output(run_config, plugin_config, metadata) as output:
            try:
                keys = reg.glob_keys(
                    "\\HKLM\\System\\*ControlSet*\\Control\\Session Manager"
                )
                for key in keys:
                    self.parse_key(key, output, report)
            except Exception as e:
                report.add_error(f"{e}")

            report.add_output_report(output.get_report())

        return report

    def parse_key(self, key: RegKey, output: Output, report: RunReport):
        try:
            pfo = key.value("PendingFileRenameOperations")
            if not pfo:
                return
            pending_ops = pfo.data()

            if not isinstance(pending_ops, list):
                return

            if len(pending_ops) % 2 != 0:
                pending_ops = pending_ops[:-1]

            for j in range(0, len(pending_ops), 2):
                tuple = Record()
                tuple.add("old_name", value(pending_ops[j]))
                tuple.add("new_name", value(pending_ops[j + 1]))
                tuple.add("key_path", value(key.path))
                tuple.add("key_modif_time", value(key.mtime))
                tuple.add(
                    "key_security", Value.Object(key.security_descriptor.to_record())
                )
                output.write(tuple)

        except Exception as e:
            report.add_error(f"{e}")
