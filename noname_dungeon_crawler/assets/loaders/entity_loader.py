import json
import pathlib
import typing
from importlib import import_module

from noname_dungeon_crawler.settings import config
from noname_dungeon_crawler.sprites import Entity


class EntityLoader:
    entity_configs: typing.List[pathlib.Path]

    def __init__(self) -> None:
        self.entity_configs = [conf for conf in config.constants.ENTITY_DIR.iterdir() if conf.is_file()]

    def load_entities(self) -> typing.Dict[str, Entity]:
        entity_module = import_module('noname_dungeon_crawler.sprites.entities')

        entities: typing.Dict[str, Entity] = {}

        for entity_config in self.entity_configs:
            with open(entity_config, 'r') as conf_file:
                conf = json.load(conf_file)

            entity_class: typing.Type[Entity] = getattr(entity_module, conf['class'])
            entity_name, entity_args = entity_class.args_from_config(conf)
            entities[entity_name] = entity_class(**entity_args)

        return entities
