import json
import logging
from datetime import datetime, timezone
from typing import List

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


class FirefoxExtension(OgrePlugin):
    def description(self) -> PluginDescription:
        return PluginDescription(
            "FirefoxExtension",
            "Get Firefox 26+ browser extensions, version after December 10, 2013",
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
                    data = json.load(input)
                    for extension in data.get("addons", []):
                        try:
                            tuple = Record()
                            tuple.add("browser", value("firefox"))
                            if "defaultLocale" in extension:
                                name = extension["defaultLocale"].get("name", None)
                                tuple.add("name", value(name))

                                description = extension["defaultLocale"].get(
                                    "description", None
                                )
                                tuple.add("description", value(description))

                            tuple.add("id", value(extension.get("id", None)))
                            tuple.add("version", value(extension.get("version", None)))
                            tuple.add("type", value(extension.get("type", None)))
                            tuple.add("path", value(extension.get("path", None)))
                            tuple.add(
                                "source_uri", value(extension.get("sourceURI", None))
                            )
                            tuple.add("root_uri", value(extension.get("rootURI", None)))
                            tuple.add(
                                "update_url", value(extension.get("updateURL", None))
                            )
                            user_permissions = self.get_permission(
                                extension.get("userPermissions", None)
                            )
                            tuple.add(
                                "user_permissions", Value.Object(user_permissions)
                            )

                            optional_permissions = self.get_permission(
                                extension.get("optionalPermissions", None)
                            )
                            tuple.add(
                                "optional_permissions",
                                Value.Object(optional_permissions),
                            )

                            requested_permissions = self.get_permission(
                                extension.get("requestedPermissions", None)
                            )
                            tuple.add(
                                "requested_permissions",
                                Value.Object(requested_permissions),
                            )

                            if "installDate" in extension:
                                install_date = datetime.fromtimestamp(
                                    extension["installDate"] / 1000, tz=timezone.utc
                                )
                                tuple.add("install_date", value(install_date))
                            if "updateDate" in extension:
                                update_date = datetime.fromtimestamp(
                                    extension["updateDate"] / 1000, tz=timezone.utc
                                )
                                tuple.add("update_date", value(update_date))

                            output.write(tuple)
                        except Exception as e:
                            logger.error(f"{e}")
                            report.add_error(f"{e}")
            except Exception as e:
                logger.error(f"{e}")
                report.add_error(f"{e}")
            report.add_output_report(output.get_report())

        return report

    def get_permission(self, json_data) -> Record:
        perm = Record()
        if not json_data:
            return perm
        if json_data.get("permissions"):
            permissions: List[Value] = []
            for permission in json_data.get("permissions"):
                permissions.append(Value.String(permission))
            perm.add("permissions", Value.Array(permissions))

        if json_data.get("origins"):
            origins: List[Value] = []
            for origin in json_data.get("origins"):
                origins.append(Value.String(origin))
            perm.add("origins", Value.Array(origins))

        if json_data.get("data_collection"):
            data_collections: List[Value] = []
            for data_collection in json_data.get("data_collection"):
                data_collections.append(Value.String(data_collection))
            perm.add("data_collection", Value.Array(data_collections))
        return perm
