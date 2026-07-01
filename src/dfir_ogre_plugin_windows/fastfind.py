from dfir_ogre_common import (
    Metadata,
    OgrePlugin,
    PluginConfiguration,
    PluginDescription,
    RunConfiguration,
    RunReport,
    parse_xml,
    win_frn_hex_parser,
    win_ntfs_flag_parser,
)

LOG_BEFORE_FAIL = 1000


class FastFind(OgrePlugin):
    def description(self) -> PluginDescription:
        return PluginDescription(
            "FastFind",
            "Parse the filesystem entries of a FastFind output",
        )

    def parse(
        self,
        input_file: str,
        plugin_file: str,
        run_config: RunConfiguration,
        metadata: Metadata,
    ) -> RunReport:
        rust_mapping = {
            "@frn": win_frn_hex_parser(""),
            "filename/@parentfrn": win_frn_hex_parser("fn_parent_"),
            "i30/@parentfrn": win_frn_hex_parser("i30_parent_"),
            "standardinformation/@attributes":win_ntfs_flag_parser()
        }
        plugin_config = PluginConfiguration.load(plugin_file, extension=rust_mapping)
        return parse_xml(
            input_file,
            run_config,
            plugin_config,
            metadata,
        )
