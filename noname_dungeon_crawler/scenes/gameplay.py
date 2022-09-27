        import typing

import arcade

from noname_dungeon_crawler.assets import asset_repository
from noname_dungeon_crawler.gui import draw_player_gui
from noname_dungeon_crawler.level_generator import LevelGenerator
from noname_dungeon_crawler.settings import config
from noname_dungeon_crawler.sprites import Entity, Player
from noname_dungeon_crawler.util import Timer, get_game

from .interactable_scene import InteractableScene
from .scene_type import SceneType


import logging

log = logging.getLogger(__name__)


class GameplayScene(InteractableScene):
    timers: typing.List[Timer]
    physics_engines: typing.Dict[Entity, arcade.PhysicsEngineSimple]

    level: int

    camera: arcade.Camera
    gui_camera: arcade.Camera

    player_entity: Player

    _mouse_pressed: bool
    _mouse_coords: typing.Tuple[int, int]

    def __init__(self) -> None:
        super().__init__(scene_type=SceneType.GAMEPLAY, music_tracks=['gameplay'])

        self.timers = []
        self.physics_engines = {}

        self._mouse_pressed = False
        self._mouse_coords = (0, 0)

        self.level = 1

        self.add_sprite_list('floor')
        self.add_sprite_list('walls')
        self.add_sprite_list('chests')
        self.add_sprite_list('mobs')
        self.add_sprite_list('doors')

        self.add_sprite_list('impassable', use_spatial_hash=True)

        self.player_entity = typing.cast(Player, asset_repository.get_entity('player'))
        self.add_sprite('player', self.player_entity)

        self.camera = arcade.Camera(*config.resolution)
        self.gui_camera = arcade.Camera(*config.resolution)

        self._init_level()

    def on_update(self, delta_time: float = 1 / 60, names: typing.Optional[typing.List[str]] = None) -> None:
        super().on_update(delta_time, names)

        for timer in self.timers:
            timer.update(delta_time)

        self.timers = [timer for timer in self.timers if not timer.finished]

        self._move_camera_to_player()
        if self._mouse_pressed:
            self.player_entity.swing_weapon(*self._project_coordinates(*self._mouse_coords))

        for physics_engine in self.physics_engines.values():
            physics_engine.update()

    def draw(self, names: typing.Optional[typing.List[str]] = None, **kwargs: typing.Any) -> None:
        self.camera.use()

        super().draw(names, **kwargs)

        for enemy in self.get_sprite_list('mobs'):
            enemy.draw_hp_bar()  # type: ignore

        self.gui_camera.use()
        draw_player_gui(self.player_entity)

    def add_timer(self, timer: Timer) -> None:
        self.timers.append(timer)

    def start_next_level(self) -> None:
        self._clear()

        self.level += 1
        self._init_level()

    def add_physics_engine(self, entity: Entity) -> arcade.PhysicsEngineSimple:
        engine = arcade.PhysicsEngineSimple(entity, self.get_sprite_list('impassable'))
        self.physics_engines[entity] = engine

        return engine

    def remove_physics_engine(self, entity: Entity) -> None:
        if entity in self.physics_engines:
            del self.physics_engines[entity]

    def _clear(self) -> None:
        self.get_sprite_list('floor').clear()
        self.get_sprite_list('walls').clear()
        self.get_sprite_list('chests').clear()
        self.get_sprite_list('mobs').clear()
        self.get_sprite_list('doors').clear()
        self.get_sprite_list('impassable').clear()

        self.physics_engines.clear()

    def _init_level(self) -> None:
        generator = LevelGenerator(level=self.level)
        level = generator.generate_level()

        self.get_sprite_list('floor').extend(level.floor)
        self.get_sprite_list('walls').extend(level.walls)
        self.get_sprite_list('chests').extend(level.chests)
        self.get_sprite_list('mobs').extend(level.mobs)
        self.get_sprite_list('doors').extend(level.doors)

        self.get_sprite_list('impassable').extend(self.get_sprite_list('walls'))
        self.get_sprite_list('impassable').extend(self.get_sprite_list('chests'))
        self.get_sprite_list('impassable').extend(self.get_sprite_list('mobs'))
        self.get_sprite_list('impassable').extend(self.get_sprite_list('doors'))

        self.player_entity.position = level.starting_coords
        self._init_physics()

    def _init_physics(self) -> None:
        self.add_physics_engine(self.player_entity)
        for mob in self.get_sprite_list('mobs'):
            self.add_physics_engine(mob)  # type: ignore

    def _get_cam_coordinates(self) -> typing.Tuple[float, float]:
        cam_center_x = self.player_entity.center_x - (self.camera.viewport_width / 2)
        cam_center_y = self.player_entity.center_y - (self.camera.viewport_height / 2)

        return cam_center_x, cam_center_y

    def _move_camera_to_player(self) -> None:
        self.camera.move_to(self._get_cam_coordinates())

    def _project_coordinates(self, x: int, y: int) -> typing.Tuple[int, int]:
        cam_center_x, cam_center_y = self._get_cam_coordinates()
        return int(x + cam_center_x), int(y + cam_center_y)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        match symbol:
            case arcade.key.W:
                self.player_entity.movement_vector[1] += 1
            case arcade.key.S:
                self.player_entity.movement_vector[1] -= 1
            case arcade.key.A:
                self.player_entity.movement_vector[0] -= 1
            case arcade.key.D:
                self.player_entity.movement_vector[0] += 1

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        match symbol:
            case arcade.key.W:
                self.player_entity.movement_vector[1] -= 1
            case arcade.key.S:
                self.player_entity.movement_vector[1] += 1
            case arcade.key.A:
                self.player_entity.movement_vector[0] += 1
            case arcade.key.D:
                self.player_entity.movement_vector[0] -= 1
            case arcade.key.ESCAPE:
                get_game().activate_scene(SceneType.PAUSE)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        self._mouse_coords = (x, y)

        if button == arcade.MOUSE_BUTTON_LEFT:
            self._mouse_pressed = True

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            self._mouse_pressed = False
        self.player_entity.swing_weapon(*self._project_coordinates(x, y))

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        self._mouse_coords = (x, y)

    def on_deactivate(self) -> None:
        super().on_deactivate()
        self.music_player.delete()
        get_game().scenes[self.scene_type] = self.__class__()
