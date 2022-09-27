import typing

import arcade

from noname_dungeon_crawler.gui import get_pause_gui
from noname_dungeon_crawler.settings import config
from noname_dungeon_crawler.util import get_game

from .interactable_scene import InteractableScene
from .scene_type import SceneType


class PauseScene(InteractableScene):
    def __init__(self) -> None:
        super().__init__(SceneType.PAUSE, ui_manager=get_pause_gui())

    def draw(self, names: typing.Optional[typing.List[str]] = None, **kwargs: typing.Any) -> None:
        # Draw overlay
        arcade.draw_rectangle_filled(
            center_x=config.resolution[0] // 2,
            center_y=config.resolution[1] // 2,
            width=config.resolution[0],
            height=config.resolution[1],
            color=(0, 0, 0, 196)
        )

        super().draw(names, **kwargs)

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        if symbol == arcade.key.ESCAPE:
            get_game().deactivate_scene()
