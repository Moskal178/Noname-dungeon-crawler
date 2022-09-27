import typing

import arcade
import arcade.gui

from noname_dungeon_crawler.gui import get_main_menu_gui
from noname_dungeon_crawler.settings import config

from .interactable_scene import InteractableScene
from .scene_type import SceneType


class MainMenuScene(InteractableScene):
    background_texture: arcade.Texture

    def __init__(self) -> None:
        from noname_dungeon_crawler.assets import asset_repository

        super().__init__(SceneType.MAIN_MENU, ui_manager=get_main_menu_gui(), music_tracks=['main_menu'])
        self.background_texture = asset_repository.get_static_texture('main_menu_back')

    def draw(self, names: typing.Optional[typing.List[str]] = None, **kwargs: typing.Any) -> None:
        arcade.draw_texture_rectangle(
            center_x=config.resolution[0] // 2,
            center_y=config.resolution[1] // 2,
            width=config.resolution[0],
            height=config.resolution[1],
            texture=self.background_texture
        )

        super().draw(names, **kwargs)
