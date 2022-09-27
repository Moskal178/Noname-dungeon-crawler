import logging
import typing

import arcade

from noname_dungeon_crawler.sprites import Entity

from .loaders import EntityLoader, SoundLoader, TextureLoader


log = logging.getLogger(__name__)


class AssetRepository:
    # Textures
    texture_atlas: arcade.TextureAtlas
    _textures_static: typing.Dict[str, arcade.Texture]
    _textures_animated: typing.Dict[str, typing.List[arcade.Texture]]

    # Sample entity index
    _entities: typing.Dict[str, Entity]

    # Sounds
    _sound_effects: typing.Dict[str, arcade.Sound]
    _music: typing.Dict[str, arcade.Sound]

    def get_static_texture(self, name: str) -> arcade.Texture:
        if name not in self._textures_static:
            raise ValueError(f"No such texture: {name}")

        return self._textures_static[name]

    def get_animated_texture(self, name: str) -> typing.List[arcade.Texture]:
        if name not in self._textures_animated:
            raise ValueError(f"No such animation: {name}")

        return self._textures_animated[name]

    def get_entity(self, name: str) -> Entity:
        if name not in self._entities:
            raise ValueError(f"No such entity: {name}")

        return self._entities[name].get_copy()

    def get_sound_effect(self, name: str) -> arcade.Sound:
        if name not in self._sound_effects:
            raise ValueError(f"No such sound effect: {name}")

        return self._sound_effects[name]

    def get_music(self, name: str) -> arcade.Sound:
        if name not in self._music:
            raise ValueError(f"No such music track: {name}")

        return self._music[name]

    def load_assets(self) -> None:
        log.info("Loading assets...")

        log.info("Loading textures...")

        texture_loader = TextureLoader()
        texture_container = texture_loader.load_textures()

        self._textures_static = texture_container.static
        self._textures_animated = texture_container.animated
        self.texture_atlas = texture_container.atlas

        log.info("Finished loading textures!")
        log.info("Loading sounds...")

        sound_loader = SoundLoader()
        self._sound_effects = sound_loader.load_effects()
        self._music = sound_loader.load_music()

        log.info("Finished loading sounds!")
        log.info("Loading entities...")

        entity_loader = EntityLoader()
        self._entities = entity_loader.load_entities()

        log.info("Finished loading entities!")
        log.info("Finished loading assets!")


asset_repository = AssetRepository()
