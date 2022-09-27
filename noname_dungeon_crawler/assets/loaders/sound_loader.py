import pathlib
import typing

import arcade

from noname_dungeon_crawler.settings import config


class SoundLoader:
    effects_path: pathlib.Path
    music_path: pathlib.Path

    def __init__(self) -> None:
        self.effects_path = config.constants.SOUND_DIR / 'effects'
        self.music_path = config.constants.SOUND_DIR / 'music'

    def load_effects(self) -> typing.Dict[str, arcade.Sound]:
        return self._load_sounds(self.effects_path, streaming=False)

    def load_music(self) -> typing.Dict[str, arcade.Sound]:
        return self._load_sounds(self.music_path, streaming=False)

    def _load_sounds(self, path: pathlib.Path, streaming: bool) -> typing.Dict[str, arcade.Sound]:
        sound_files = [f for f in path.iterdir() if f.is_file()]
        return {sound_file.stem: arcade.load_sound(sound_file, streaming=streaming) for sound_file in sound_files}  # type: ignore
