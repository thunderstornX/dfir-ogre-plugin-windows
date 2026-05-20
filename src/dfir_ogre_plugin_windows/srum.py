from dfir_ogre_common import (
    Metadata,
    OgrePlugin,
    PluginConfiguration,
    PluginDescription,
    RunConfiguration,
    RunReport,
    parse_srum,
)


class Srum(OgrePlugin):
    def description(self) -> PluginDescription:
        return PluginDescription(
            "Srum",
            "SRUM (System Resource Usage Monitor) database file parser",
        )

    def parse(
        self,
        input_file: str,
        plugin_file: str,
        run_config: RunConfiguration,
        metadata: Metadata,
    ) -> RunReport:
        plugin_config = PluginConfiguration.load(plugin_file)
        return parse_srum(input_file, run_config, plugin_config, metadata)
