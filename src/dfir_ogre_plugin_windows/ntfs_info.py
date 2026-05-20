from typing import List, Optional

from dfir_ogre_common import (
    AbstractParser,
    FieldName,
    Metadata,
    OgrePlugin,
    PluginConfiguration,
    PluginDescription,
    Qualifiers,
    Record,
    RunConfiguration,
    RunReport,
    Value,
    parse_csv,
    win_frn_hex_parser,
    win_ntfs_flag_parser,
    win_signed_hash_parser,
)

Qualifier = Qualifiers()

LOG_BEFORE_FAIL = 1000


class NTFSInfo(OgrePlugin):
    def description(self) -> PluginDescription:
        return PluginDescription(
            "NTFSInfo",
            "NTFSInfo parser.",
        )

    def parse(
        self,
        input_file: str,
        plugin_file: str,
        run_config: RunConfiguration,
        metadata: Metadata,
    ) -> RunReport:
        rust_mapping = {
            "Attributes": win_ntfs_flag_parser(),
            "FRN": win_frn_hex_parser(""),
            "SignedHash": win_signed_hash_parser(),
        }
        plugin_config = PluginConfiguration.load(plugin_file, extension=rust_mapping)
        return parse_csv(
            input_file,
            run_config,
            plugin_config,
            metadata,
            LOG_BEFORE_FAIL,
        )


class SignedHashParser(AbstractParser):
    """Cast the value of SignedHash field into the right hash"""

    md5 = FieldName("file_pe_md5", qualifier=Qualifier.PE_MD5)
    sha1 = FieldName("file_pe_sha1", qualifier=Qualifier.PE_SHA1)
    sha256 = FieldName("file_pe_sha256", qualifier=Qualifier.PE_SHA256)

    def parse(self, input: str, ouput_name: str) -> Optional[Record]:
        if not input:
            return
        match len(input):
            case 32:
                tuple = Record()
                tuple.add(self.md5.output_name(), Value.String(input))
                return tuple

            case 40:
                tuple = Record()
                tuple.add(self.sha1.output_name(), Value.String(input))
                return tuple
            case 64:
                tuple = Record()
                tuple.add(self.sha256.output_name(), Value.String(input))
                return tuple

    def output_fields_names(self) -> List[FieldName]:
        return [self.md5, self.sha1, self.sha256]
