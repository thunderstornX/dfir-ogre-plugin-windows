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

from dfir_ogre_plugin_windows.common import filetime_to_utc, value

logger = logging.getLogger(__name__)


class RegRecentApp(OgrePlugin):
    def description(self) -> PluginDescription:
        return PluginDescription(
            "RegRecentApp",
            "(no test data) Get informations about applications and files accessed (windows >=10) from NTUser",
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

        with Output(
            run_config,
            plugin_config,
            metadata,
        ) as output:
            try:
                keys = reg.glob_keys(
                    "\\HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Search\\RecentApps\\*"
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

            guid_app = uuid.UUID(key.name[1:-1])
            tuple.add("guid_app", value(str(guid_app)))

            app_id = key.value_data("AppId")
            tuple.add("app_id", value(app_id))

            launch_count = key.value_data("LaunchCount")
            tuple.add("launch_count", value(launch_count))

            app_last_accessed_time_int = key.value_data("LastAccessedTime")
            if app_last_accessed_time_int:
                app_last_accessed_time = filetime_to_utc(app_last_accessed_time_int)
                tuple.add("app_last_accessed_time", value(app_last_accessed_time))

            try:
                recent_items = key.sub_key("RecentItems")
                if recent_items:
                    for item in recent_items.sub_keys():
                        guid_file = uuid.UUID(item.name[1:-1])
                        tuple.add("guid_file", value(str(guid_file)))

                        display_name = item.value_data("DisplayName")
                        tuple.add("display_name", value(display_name))

                        path = item.value_data("Path")
                        arguments = item.value_data("Arguments")
                        path = f"{path} {arguments}"
                        tuple.add("path", value(path))

                        file_last_accessed_time_int = item.value_data(
                            "LastAccessedTime"
                        )
                        if file_last_accessed_time_int:
                            file_last_accessed_time = filetime_to_utc(
                                file_last_accessed_time_int
                            )
                            tuple.add(
                                "file_last_accessed_time",
                                value(file_last_accessed_time),
                            )

                        tuple.add("key_path", value(item.path))
                        tuple.add("key_modif_time", value(item.mtime))
                        tuple.add(
                            "key_security",
                            Value.Object(item.security_descriptor.to_record()),
                        )
            except Exception:
                tuple.add("key_path", value(key.path))
                tuple.add("key_modif_time", value(key.mtime))
                tuple.add(
                    "key_security",
                    Value.Object(key.security_descriptor.to_record()),
                )

            output.write(tuple)
        except Exception as e:
            report.add_error(f"{e}")
