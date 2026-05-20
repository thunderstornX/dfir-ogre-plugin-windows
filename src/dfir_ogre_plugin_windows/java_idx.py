import logging
import os
from datetime import datetime, timezone
from io import BufferedReader

import pytz
from dateutil import parser as du_parser
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

from dfir_ogre_plugin_windows.common import value

logger = logging.getLogger(__name__)


class JavaIdx(OgrePlugin):
    def description(self) -> PluginDescription:
        return PluginDescription(
            "JavaIdx",
            "Retrieve downloaded files from Java Idx",
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
                    tuple = Record()
                    #   Fields busy and incomplete are normally 0x00.
                    #   They are set to 0x01 if the file is currently being downloaded.
                    busy = parse_bool(input)
                    incomplete = parse_bool(input)

                    if busy or incomplete:
                        tuple.add("is_incomplete", value(True))

                    idx_version = int.from_bytes(
                        input.read(4), byteorder="big", signed=False
                    )

                    # idx_version is the file version
                    if idx_version not in [602, 603, 604, 605]:
                        raise ValueError(
                            f"Not a valid Java IDX file: unknown version: {idx_version}"
                        )

                    if idx_version == 602:
                        field_count = self.process_section_602(input, tuple)
                    else:
                        # IDX 6.03 and 6.04 have 16 unused bytes before the structure.
                        if idx_version in [603, 604]:
                            self._unused_603_604 = input.read(16)

                        field_count = self.process_section_605(input, tuple)

                    # File offset is now just prior to HTTP headers.
                    request = Record()
                    self.parse_request(input, request, field_count)
                    tuple.add("request", Value.Object(request))
                    output.write(tuple)

            except Exception as e:
                logger.error(f"{e}")
                report.add_error(f"{e}")
            report.add_output_report(output.get_report())

        return report

    def parse_request(self, input, record, field_count):
        tzdict = dict()
        for _ in range(0, field_count):
            field_size = int.from_bytes(input.read(2), byteorder="big", signed=False)
            field_name = input.read(field_size).decode()
            value_size = int.from_bytes(input.read(2), byteorder="big", signed=False)
            value_str = input.read(value_size).decode()

            if field_name == "date":
                try:
                    tmp_download_date = du_parser.parse(value_str)
                except ValueError as e:
                    logger.debug('Unable to parse date "%s": %s', value_str, e)
                else:
                    if tmp_download_date.tzname() is not None:
                        download_date = tmp_download_date.astimezone(timezone.utc)
                    else:
                        # However, there are a few cases where the parser does not recognize the timezone abbreviation.
                        # In these cases, the timezone abbreviation is extracted manually (it is assumed to be in last
                        # position). Then pytz is used to search through all known timezone abbreviations. The search
                        # stops after the first match and send_date is localized with the matching timezone (which is
                        # stored in a dict to avoid searching for it again the next time)
                        tzAbbr = value_str.split(" ")[-1]
                        if tzAbbr.isalpha():
                            tzAbbr = value_str.split(" ")[-1]
                            if tzAbbr in tzdict:
                                logger.warning(
                                    "Reusing previously found timezone %s matching %s for date %s",
                                    tzdict[tzAbbr].zone,
                                    tzAbbr,
                                    tmp_download_date,
                                )
                                download_date = (
                                    tzdict[tzAbbr]
                                    .localize(tmp_download_date)
                                    .astimezone(timezone.utc)
                                )
                            else:
                                download_date = None
                                for zone in pytz.all_timezones:
                                    tz = pytz.timezone(zone)
                                    if tz.tzname(tmp_download_date) == tzAbbr:
                                        logger.debug(
                                            "Found new timezone %s matching %s for date %s",
                                            tz.zone,
                                            tzAbbr,
                                            tmp_download_date,
                                        )
                                        download_date = tz.localize(
                                            tmp_download_date
                                        ).astimezone(timezone.utc)
                                        tzdict[tzAbbr] = tz
                                        break
                                if not download_date:
                                    logger.debug(
                                        'Failed to parse timezone information out of "%s" (%s). '
                                        "Be careful when interpreting this date!",
                                        value_str,
                                        tmp_download_date,
                                    )
                                    download_date = tmp_download_date.replace(
                                        tzinfo=timezone.utc
                                    )

                        else:
                            # dateutil.parser failed to parse timezone and we failed to manually detect it too. The date
                            # will be stored "as is" but the analyst must be warned that this date will NOT be UTC !
                            logger.debug(
                                'Failed to parse timezone information out of "%s" (%s). '
                                "Be careful when interpreting this date!",
                                value_str,
                                tmp_download_date,
                            )
                            download_date = tmp_download_date.replace(
                                tzinfo=timezone.utc
                            )
                    record.add("download_date", value(download_date))
            else:
                record.add(field_name, value(value_str))

    def process_section_602(self, input: BufferedReader, tuple: Record) -> int:
        # ignore the first two bytes
        _skip = input.read(2)
        tuple.add("is_shortcut", value(parse_bool(input)))

        content_length = int.from_bytes(input.read(4), byteorder="big", signed=False)
        tuple.add("content_length", value(content_length))
        tuple.add("last_modified_date", value(parse_date(input)))
        tuple.add("expiration_date", value(parse_date(input)))
        tuple.add("version_string", value(parse_string(input)))
        tuple.add("url", value(parse_string(input)))
        tuple.add("namespace", value(parse_string(input)))

        return int.from_bytes(input.read(4), byteorder="big", signed=False)

    def process_section_605(self, input: BufferedReader, tuple: Record) -> int:
        tuple.add("is_shortcut", value(parse_bool(input)))

        content_length = int.from_bytes(input.read(4), byteorder="big", signed=False)
        tuple.add("content_length", value(content_length))
        tuple.add("last_modified_date", value(parse_date(input)))
        tuple.add("expiration_date", value(parse_date(input)))
        tuple.add("validation_date", value(parse_date(input)))
        tuple.add("signed", value(parse_bool(input)))

        try:
            # Static offset for section 2.
            input.seek(128, os.SEEK_SET)
            tuple.add("version_string", value(parse_string(input)))
            tuple.add("url", value(parse_string(input)))
            tuple.add("namespace", value(parse_string(input)))
            tuple.add("ip_address", value(parse_string(input)))
            field_count = int.from_bytes(input.read(4), byteorder="big", signed=False)

        except ValueError:
            tuple.add("url", value("Unknown"))
            tuple.add("ip_address", value("Unknown"))
            field_count = 0
        return field_count


def parse_string(input: BufferedReader) -> str:
    value_size = int.from_bytes(input.read(2), byteorder="big", signed=False)
    return input.read(value_size).decode()


def parse_date(input: BufferedReader) -> datetime:
    date_ms = int.from_bytes(input.read(8), byteorder="big", signed=False)
    return datetime.fromtimestamp(date_ms / 1000.0, tz=timezone.utc)


def parse_bool(input: BufferedReader) -> bool:
    val = int.from_bytes(input.read(1), byteorder="big", signed=False)
    if val > 0:
        return True
    return False
