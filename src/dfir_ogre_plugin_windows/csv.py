from dfir_ogre_common import (
    Metadata,
    OgrePlugin,
    PluginConfiguration,
    PluginDescription,
    RunConfiguration,
    RunReport,
    parse_csv,
)
from typing_extensions import override

LOG_BEFORE_FAIL = 100


class Csv(OgrePlugin):
    @override
    def description(self) -> PluginDescription:
        return PluginDescription(
            "Csv",
            "A generic Csv parser (does not support python ot rust extension parsers).",
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
        return parse_csv(
            input_file, run_config, plugin_config, metadata, LOG_BEFORE_FAIL
        )
