import json
import logging
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
from typing_extensions import override

logger = logging.getLogger(__name__)


class ChromeExtension(OgrePlugin):
    @override
    def description(self) -> PluginDescription:
        return PluginDescription(
            "ChromeExtension",
            "Get Chrome based browser extensions",
        )

    @override
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
                    extension = json.load(input)

                    tuple = Record()
                    tuple.add(
                        "default_locale",
                        value(extension.get("default_locale", None)),
                    )
                    if "content_security_policy" in extension:
                        extension_pages = extension["content_security_policy"].get(
                            "extension_pages", None
                        )
                        tuple.add("extension_pages", value(extension_pages))

                    name = extension.get("name", None)
                    # try to find another name
                    if not name or name.startswith("__MSG_"):
                        if "action" in extension:
                            title = extension["action"].get("default_title", None)
                            if title:
                                name = title

                    tuple.add("name", value(name))

                    tuple.add("version", value(extension.get("version", None)))
                    tuple.add("description", value(extension.get("description", None)))

                    tuple.add("update_url", value(extension.get("update_url", None)))

                    permissions_array = extension.get("permissions", [])
                    permissions: List[Value] = []
                    for perm in permissions_array:
                        permissions.append(Value.String(perm))
                    tuple.add("permissions", Value.Array(permissions))

                    host_permissions_array = extension.get("host_permissions", [])
                    host_permissions: List[Value] = []
                    for perm in host_permissions_array:
                        host_permissions.append(Value.String(perm))
                    tuple.add("host_permissions", Value.Array(host_permissions))

                    optional_permissions_array = extension.get(
                        "optional_permissions", []
                    )
                    optional_permissions: List[Value] = []
                    for perm in optional_permissions_array:
                        optional_permissions.append(Value.String(perm))
                    tuple.add("optional_permissions", Value.Array(optional_permissions))

                    output.write(tuple)

            except Exception as e:
                report.add_error(f"{e}")  # pyright: ignore[reportUnknownMemberType]
            report.add_output_report(output.get_report())

        return report
