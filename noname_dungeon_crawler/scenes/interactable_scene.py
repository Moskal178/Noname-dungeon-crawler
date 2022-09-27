import typing

import arcade
import arcade.gui
import pyglet.media

from noname_dungeon_crawler.settings import config

from .scene_type import SceneType


class InteractableScene(arcade.Scene):
    """
    Базовый класс с утилитарными методами, который наследует оригинальную сцену из arcade
    """
    scene_type: SceneType
    ui_manager: arcade.gui.UIManager

    music_player: pyglet.media.Player
    music_tracks: typing.List[arcade.Sound]

    def __init__(
        self,
        scene_type: SceneType,
        ui_manager: typing.Optional[arcade.gui.UIManager] = None,
        music_tracks: typing.List[str] = [],
    ) -> None:
        from noname_dungeon_crawler.assets import asset_repository

        super().__init__()

        self.scene_type = scene_type

        if not ui_manager:
            ui_manager = arcade.gui.UIManager()
        self.ui_manager = ui_manager

        self.music_tracks = [asset_repository.get_music(track) for track in music_tracks]
        self.music_player = pyglet.media.Player()
        self._reset_player()
        self.music_player.loop = True
        self.music_player.volume = config.music_volume

    def draw(self, names: typing.Optional[typing.List[str]] = None, **kwargs: typing.Any) -> None:
        super().draw(names, **kwargs)

        self.ui_manager.draw()

    def _reset_player(self) -> None:
        for track in self.music_tracks:
            self.music_player.queue(track.source)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        pass

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        pass

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        pass

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        pass

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        pass

    def on_activate(self) -> None:
        self.ui_manager.enable()
        self.music_player.play()

    def on_deactivate(self) -> None:
        self.ui_manager.disable()
        self.music_player.pause()
