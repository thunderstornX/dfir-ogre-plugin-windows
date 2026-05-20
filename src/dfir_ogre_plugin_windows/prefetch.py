import logging
from datetime import datetime, timezone
from typing import List

import pyscca
from dfir_ogre_common import (
    Metadata,
    OgrePlugin,
    Output,
    PluginConfiguration,
    PluginDescription,
    Record,
    RunConfiguration,
    RunReport,
    Value,
)

from dfir_ogre_plugin_windows.common import filetime_to_utc, value

logger = logging.getLogger(__name__)


class Prefetch(OgrePlugin):
    def description(self) -> PluginDescription:
        return PluginDescription(
            "Prefetch",
            "Parse the windows prefetch files",
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

        with Output(run_config, plugin_config, metadata) as output:
            try:
                with open(input_file, "rb") as input:
                    prefetch = pyscca.file()
                    prefetch.open_file_object(input)

                    for i in range(prefetch.run_count):
                        tuple = Record()
                        date = filetime_to_utc(prefetch.get_last_run_time_as_integer(i))
                        tuple.add("run_date", value(date))
                        tuple.add("executable", value(prefetch.executable_filename))
                        tuple.add("version", value(str(prefetch.format_version)))
                        tuple.add("prefetch_hash", value(prefetch.prefetch_hash))
                        tuple.add("run_count", value(prefetch.run_count))
                        tuple.add(
                            "file_count", value(prefetch.number_of_file_metrics_entries)
                        )
                        tuple.add("volume_count", value(prefetch.number_of_volumes))

                        files = self.parse_files(prefetch)
                        tuple.add("files", Value.Array(files))

                        volumes = []
                        path_hints = []
                        self.parse_volumes(prefetch, volumes, path_hints)
                        tuple.add("volumes", Value.Array(volumes))
                        tuple.add("path_hints", Value.Array(path_hints))

                        output.write(tuple)

            except Exception as e:
                report.add_error(f"{e}")
            report.add_output_report(output.get_report())

        return report

    def parse_volumes(self, prefetch, volumes: List[Value], path_hints: List[Value]):
        for volume_information in iter(prefetch.volumes):
            volume_entry = Record()
            volume_entry.add("path", value(volume_information.device_path))
            volume_entry.add("serial_number", value(volume_information.serial_number))

            creation_time = volume_information.creation_time
            if isinstance(creation_time, datetime):
                creation_time = creation_time.replace(tzinfo=timezone.utc)

            volume_entry.add("creation_time", value(creation_time))

            volumes.append(Value.Object(volume_entry))

            for filename in iter(prefetch.filenames):
                if (
                    filename
                    and filename.startswith(volume_information.device_path)
                    and filename.endswith(prefetch.executable_filename)
                ):
                    _, _, path = filename.partition(volume_information.device_path)
                    path_hints.append(value(path))

    def parse_files(self, prefetch) -> List[Value]:
        files = []
        for entry_index, file_metrics in enumerate(prefetch.file_metrics_entries):
            file_entry = Record()
            file_entry.add("index", value(entry_index))
            file_entry.add("path", value(file_metrics.filename))
            reference = file_metrics.file_reference
            if reference:
                try:
                    frn = (
                        f"0x{reference >> 48:0{4}X}{reference & 0xFFFFFFFFFFFF:0{12}X}"
                    )
                    file_entry.add("frn", value(frn))
                    sequence_number = int(frn[2:6], base=16)
                    file_entry.add("sequence_number", value(sequence_number))
                    record_number = int(frn[6:], base=16)
                    file_entry.add("record_number", value(record_number))
                except ValueError:
                    # Ignore error
                    ...

            files.append(Value.Object(file_entry))
        return files
