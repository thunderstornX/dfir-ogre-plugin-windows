from dfir_ogre_common import (
    Metadata,
    OgrePlugin,
    PluginConfiguration,
    PluginDescription,
    RunConfiguration,
    RunReport,
    parse_json,
)

LOG_BEFORE_FAIL = 100


class Json(OgrePlugin):
    def description(self) -> PluginDescription:
        return PluginDescription(
            "Json",
            "Extract data from a JSON File",
        )

    def parse(
        self,
        input_file: str,
        plugin_file: str,
        run_config: RunConfiguration,
        metadata: Metadata,
    ) -> RunReport:
        plugin_config = PluginConfiguration.load(plugin_file)
        return parse_json(input_file, run_config, plugin_config, metadata)
