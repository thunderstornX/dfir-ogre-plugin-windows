from dfir_ogre_common import (
    Metadata,
    OgrePlugin,
    PluginConfiguration,
    PluginDescription,
    RunConfiguration,
    RunReport,
    parse_regexp,
)

LOG_BEFORE_FAIL = 100


class RegExp(OgrePlugin):
    def description(self) -> PluginDescription:
        return PluginDescription(
            "Regexp",
            "A generic text file parser using a regexp",
        )

    def parse(
        self,
        input_file: str,
        plugin_file: str,
        run_config: RunConfiguration,
        metadata: Metadata,
    ) -> RunReport:
        plugin_config = PluginConfiguration.load(plugin_file)

        return parse_regexp(
            input_file, run_config, plugin_config, metadata, LOG_BEFORE_FAIL
        )
