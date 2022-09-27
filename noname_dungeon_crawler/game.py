import collections
import logging
import typing

import arcade

from .assets import asset_repository
from .scenes import GameplayScene, InteractableScene, MainMenuScene, PauseScene, SceneType
from .settings import config


log = logging.getLogger(__name__)


WINDOW_TITLE = "NoName Dungeon Crawler"


class NonameDungeonCrawler(arcade.Window):
    """
    Инициализация сцен и эвентов управления.
    """
    scenes: typing.Dict[SceneType, InteractableScene]
    active_scenes: typing.Deque[InteractableScene]

    _instance: 'NonameDungeonCrawler'

    def __init__(self) -> None:
        super().__init__(*config.resolution, WINDOW_TITLE)

        arcade.set_background_color(arcade.csscolor.BLACK)

        self.__class__._instance = self

    def setup(self) -> None:
        log.info("Starting game...")

        asset_repository.load_assets()

        self.scenes = collections.OrderedDict()
        self.scenes[SceneType.MAIN_MENU] = MainMenuScene()
        self.scenes[SceneType.GAMEPLAY] = GameplayScene()
        self.scenes[SceneType.PAUSE] = PauseScene()

        self.active_scenes = collections.deque()
        self.activate_scene(SceneType.MAIN_MENU)

    def activate_scene(self, scene_type: SceneType, clear: bool = False) -> None:
        if clear:
            for _ in range(len(self.active_scenes)):
                self.deactivate_scene()

        scene = self.scenes[scene_type]
        self.active_scenes.append(scene)
        scene.on_activate()

    def deactivate_scene(self) -> None:
        scene = self.active_scenes.pop()
        scene.on_deactivate()

    def get_gameplay_scene(self) -> GameplayScene:
        return self.scenes[SceneType.GAMEPLAY]  # type: ignore

    def on_draw(self) -> None:
        self.clear()

        for scene in self.active_scenes:
            scene.draw(pixelated=True)

    def on_update(self, delta_time: float) -> None:
        scene = self.active_scenes[-1]
        scene.on_update(delta_time)
        scene.update_animation(delta_time)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        scene = self.active_scenes[-1]
        scene.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        scene = self.active_scenes[-1]
        scene.on_key_release(symbol, modifiers)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        scene = self.active_scenes[-1]
        scene.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        scene = self.active_scenes[-1]
        scene.on_mouse_release(x, y, button, modifiers)

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int) -> None:
        scene = self.active_scenes[-1]
        scene.on_mouse_motion(x, y, dx, dy)

    @classmethod
    def get_instance(cls) -> 'NonameDungeonCrawler':
        return cls._instance
