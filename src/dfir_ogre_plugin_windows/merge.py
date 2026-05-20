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


class MergeLine(OgrePlugin):
    def description(self) -> PluginDescription:
        return PluginDescription(
            "Merge", "Merge every text lines into a single output line"
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
        with open(input_file) as input:
            with Output(run_config, plugin_config, metadata) as output:
                tuple = Record()
                line = "".join([line for line in input])
                tuple.add("data", Value.String(line.strip()))
                output.write(tuple)

        report.add_output_report(output.get_report())
        return report
