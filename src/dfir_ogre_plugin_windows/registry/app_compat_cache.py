import io
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

from dfir_ogre_plugin_windows.common import filetime_to_utc, value

logger = logging.getLogger(__name__)


class RegAppCompatCache(OgrePlugin):
    def description(self) -> PluginDescription:
        return PluginDescription(
            "RegAppCompatCache",
            "Get the Application Compatibility cache from System hive",
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
            reg = Registry.load(input_file, "\\HKLM\\SYSTEM")
        except Exception as e:
            report.add_error(f"{e}")
            return report

        with Output(run_config, plugin_config, metadata) as output:
            try:
                keys = reg.glob_keys(
                    "\\HKLM\\SYSTEM\\*ControlSet*\\Control\\Session Manager\\AppCompatCache"
                )
                for key in keys:
                    self.parse_key(key, output, report)
            except Exception as e:
                report.add_error(f"{e}")

            report.add_output_report(output.get_report())

        return report

    def parse_key(self, key: RegKey, output: Output, report: RunReport):
        try:
            cache_key = key.value("AppCompatCache")

            if cache_key and isinstance(cache_key.data(), bytes):
                cache = cache_key.data()
                sig = cache[0:4].hex()
                # windows8
                if sig in ["00000000", "80000000"]:
                    header_size = 128
                # windows10
                elif sig in ["30000000", "34000000"]:
                    header_size = int.from_bytes(cache[0:4], byteorder="little")
                else:
                    header_size = 8
                i = 0
                index = header_size
                while index < len(cache):
                    # check signature
                    if cache[index : index + 4] == b"10ts":
                        entry_size = int.from_bytes(
                            cache[index + 8 : index + 8 + 4], byteorder="little"
                        )

                        tuple = Record()
                        tuple.add("index", value(i))
                        record = io.BytesIO(cache[index + 12 : index + 12 + entry_size])

                        path_size = int.from_bytes(record.read(2), byteorder="little")
                        path = record.read(path_size).decode("utf-16-le")
                        tuple.add("path", value(path))

                        # windows8 need to skip 10 bytes
                        if sig in ["00000000", "80000000"]:
                            record.read(2)
                            tuple.add("flag1", value(record.read(4)))
                            tuple.add("flag2", value(record.read(4)))

                        filetime = int.from_bytes(record.read(8), byteorder="little")
                        modification_date = filetime_to_utc(filetime)
                        tuple.add("modification_date", value(modification_date))

                        tuple.add("key_path", value(key.path))
                        tuple.add("key_modif_time", value(key.mtime))
                        tuple.add(
                            "key_security",
                            Value.Object(key.security_descriptor.to_record()),
                        )
                        output.write(tuple)
                        i += 1
                        index += 12 + entry_size
                    else:
                        index += 1

        except Exception as e:
            report.add_error(f"{e}")
