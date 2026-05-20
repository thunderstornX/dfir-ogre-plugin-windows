from dfir_ogre_common import (
    Metadata,
    OgrePlugin,
    PluginConfiguration,
    PluginDescription,
    RunConfiguration,
    RunReport,
    parse_jsonl,
)

LOG_BEFORE_FAIL = 100


class Jsonl(OgrePlugin):
    def description(self) -> PluginDescription:
        return PluginDescription(
            "Jsonl",
            "Extract data from a JSONL File",
        )

    def parse(
        self,
        input_file: str,
        plugin_file: str,
        run_config: RunConfiguration,
        metadata: Metadata,
    ) -> RunReport:
        plugin_config = PluginConfiguration.load(plugin_file)
        return parse_jsonl(input_file, run_config, plugin_config, metadata)
