import logging

from dfir_ogre_common import (
    Metadata,
    OgrePlugin,
    Output,
    PluginConfiguration,
    PluginDescription,
    Record,
    RunConfiguration,
    RunReport,
)

from dfir_ogre_plugin_windows.common import filetime_to_utc, value

logger = logging.getLogger(__name__)


class RecycleBin(OgrePlugin):
    def description(self) -> PluginDescription:
        return PluginDescription(
            "RecycleBin",
            "Retrieve file information from the recycle bin",
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

        with Output(
            run_config,
            plugin_config,
            metadata,
        ) as output:
            try:
                with open(input_file, "rb") as input:
                    tuple = Record()

                    header = int.from_bytes(input.read(8), byteorder="little")
                    tuple.add("header", value(header))

                    size = int.from_bytes(input.read(8), byteorder="little")
                    tuple.add("size", value(size))

                    deletion_timestamp_int = int.from_bytes(
                        input.read(8), byteorder="little"
                    )
                    deletion_timestamp = filetime_to_utc(deletion_timestamp_int)
                    tuple.add("uninstall_date", value(deletion_timestamp))

                    if header == 1:
                        logger.debug(
                            "INFO2 file version 1 : Windows Vista or Windows 7"
                        )
                        filepath = input.read(520)

                    elif header == 2:
                        logger.debug("INFO2 file version 2 : Windows 10+")
                        filepath_length = int.from_bytes(
                            input.read(4), byteorder="little"
                        )
                        filepath = input.read(filepath_length * 2)

                    else:
                        logger.debug("Unexpected header value: %s", header)
                        raise ValueError("Unexpected header value: %s", header)

                    path = filepath.decode(encoding="utf-16-le").replace("\u0000", "")
                    tuple.add("path", value(path))
                    output.write(tuple)

            except Exception as e:
                report.add_error(f"{e}")
            report.add_output_report(output.get_report())

        return report
