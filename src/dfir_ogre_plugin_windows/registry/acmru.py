import logging
from datetime import datetime, timezone

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


class RegAcMru(OgrePlugin):
    def description(self) -> PluginDescription:
        return PluginDescription(
            "RegAcMru",
            "(no test data) Get search request from 'search assistant' for each user",
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

        with Output(run_config, plugin_config, metadata, None) as output:
            try:
                keys = reg.glob_keys(
                    "\\HKCU\\Software\\Microsoft\\Search Assistant\\ACMru\\*"
                )
                for key in keys:
                    self.parse_key(key, output, report)
            except Exception as e:
                report.add_error(f"{e}")
            report.add_output_report(output.get_report())

        return report

    def parse_key(self, key: RegKey, output: Output, report: RunReport):
        try:
            for val in key.values():
                tuple = Record()

                tuple.add("search_request", value(val.data()))
                tuple.add("order_index", value(val.name()))

                tuple.add("key_path", value(key.path))
                tuple.add("key_modif_time", value(key.mtime))
                tuple.add(
                    "key_security", Value.Object(key.security_descriptor.to_record())
                )
                output.write(tuple)
        except Exception as e:
            # traceback.print_exception(e)

            report.add_error(f"{e}")


def parse_date(date) -> datetime | None:
    if date:
        if isinstance(date, str):
            f = "%m/%d/%Y %H:%M:%S"
            dt = datetime.strptime(date, f)
            return dt.replace(tzinfo=timezone.utc)
        else:
            return datetime.fromtimestamp(date, tz=timezone.utc)


def parse_int(value) -> int | None:
    if value:
        if isinstance(value, str):
            return int(value, base=16)
        elif isinstance(value, int):
            return value
