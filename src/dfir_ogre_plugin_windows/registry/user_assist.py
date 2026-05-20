import codecs
import logging
from datetime import datetime, timedelta
from typing import List

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

from dfir_ogre_plugin_windows.common import filetime_to_utc
from dfir_ogre_plugin_windows.know_artefacts import WIN_KNOWN_FOLDERS

logger = logging.getLogger(__name__)


class RegUserAssist(OgrePlugin):
    def description(self) -> PluginDescription:
        return PluginDescription(
            "RegUserAssist",
            "Get UserAssist entries from NTUser hive ",
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
                    "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\UserAssist\\*"
                )
                self.parse_keys(output, keys, report)

            except Exception as e:
                report.add_error(f"{e}")

        report.add_output_report(output.get_report())

        return report

    def parse_keys(self, output: Output, keys: List[RegKey], report: RunReport):
        for key in keys:
            try:
                for subkey in key.sub_keys():
                    if subkey.name == "Count":
                        for value in subkey.values():
                            name = value.name()
                            program_name = decode_rot13(name)
                            launch_type = None
                            session: int = 0
                            last_executed: datetime | None = None
                            run = 0
                            focus_count: int | None = None
                            focus_time: str | None = None

                            data = value.data()

                            if len(data) == 16:
                                index = program_name.find(":")

                                if program_name.startswith("UEME") and index > 0:
                                    launch_type = program_name[0:index]
                                    program_name = program_name[index + 1 :]

                                self.session = int.from_bytes(
                                    data[0:4], byteorder="little"
                                )

                                run = int.from_bytes(data[4:8], byteorder="little")
                                # run count is offset by 5
                                run = run - 5

                                file_time = int.from_bytes(
                                    data[8:16], byteorder="little"
                                )
                                if file_time:
                                    last_executed = filetime_to_utc(file_time)

                            elif len(value.data()) == 72:
                                if program_name.startswith("{"):
                                    kfid = program_name[1 : program_name.find("}")]
                                    kf = WIN_KNOWN_FOLDERS.get(kfid.upper())
                                    if kf:
                                        program_name = program_name.replace(kfid, kf)

                                run = int.from_bytes(data[4:8], byteorder="little")

                                focus_count = int.from_bytes(
                                    data[8:12], byteorder="little"
                                )
                                focus_time = str(
                                    timedelta(
                                        milliseconds=int.from_bytes(
                                            data[12:16], byteorder="little"
                                        )
                                    )
                                )

                                file_time = int.from_bytes(
                                    data[60:68], byteorder="little"
                                )
                                if file_time:
                                    last_executed = filetime_to_utc(file_time)

                            tuple = Record()
                            tuple.add(
                                "program_name",
                                Value.String(program_name),
                            )
                            if launch_type:
                                tuple.add(
                                    "launch_type",
                                    Value.String(launch_type),
                                )

                            tuple.add(
                                "run",
                                Value.Int(int(run)),
                            )

                            if focus_count:
                                tuple.add(
                                    "focus_count",
                                    Value.Int(focus_count),
                                )

                            if focus_time:
                                tuple.add(
                                    "focus_time",
                                    Value.String(focus_time),
                                )

                            tuple.add(
                                "session",
                                Value.Int(int(session)),
                            )

                            if last_executed:
                                tuple.add(
                                    "last_executed",
                                    Value.Date(last_executed),
                                )
                            else:
                                tuple.add("key_modif_time", Value.Date(subkey.mtime))

                            tuple.add("key_path", Value.String(key.path))

                            tuple.add(
                                "key_security",
                                Value.Object(subkey.security_descriptor.to_record()),
                            )
                            output.write(tuple)

            except Exception as e:
                report.add_error(f"{e}")


def decode_rot13(encoded_str: str):
    """UserAssist registry values are rot-13 encoded for standard ascii characters
    Unicode characters seem to be left unencoded, hence the char-by-char decoding."""
    decoded_str = ""
    try:
        decoded_str = codecs.decode(encoded_str, "rot13")
    except UnicodeEncodeError:
        for c in encoded_str:
            try:
                decoded_str += codecs.decode(c, "rot13")
            except UnicodeEncodeError:
                decoded_str += c
    return decoded_str
