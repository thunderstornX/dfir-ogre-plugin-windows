import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import TestCase

import dfir_ogre_plugin_windows  # noqa: F401
from dfir_ogre_common import OgreBatchedPlugin, OgrePlugin

from . import CONF_FOLDER


class ConfigurationTest(TestCase):
    def test_all_configuration_parsers_are_registered(self):
        registered = {
            parser().description().get_command()
            for parser in OgrePlugin.__subclasses__()
        }
        registered.update(
            parser().description().get_command()
            for parser in OgreBatchedPlugin.__subclasses__()
        )

        unknown = []
        for plugin_file in sorted(Path(CONF_FOLDER).rglob("*.xml")):
            parser = ET.parse(plugin_file).getroot().attrib.get("parser")
            if parser not in registered:
                unknown.append(f"{plugin_file}: {parser}")

        self.assertEqual([], unknown)
