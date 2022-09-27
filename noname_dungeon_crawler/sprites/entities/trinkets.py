import functools
import math
import random

import arcade

from noname_dungeon_crawler.settings import config
from noname_dungeon_crawler.sprites import Animation
from noname_dungeon_crawler.util import Timer, get_angle, get_gameplay_scene, get_player, get_vector_from_angle

from .entity import MovingEntity
from .entity_states import EntityDirection, EntityState
from .player import Player


class Trinket(MovingEntity):
    origin: arcade.Point
    is_timed: bool

    def __init__(
        self, origin: arcade.Point, level: int, animation: Animation, is_timed: bool = True, scale: float = 0.3
    ) -> None:
        self.origin = origin
        self.is_timed = is_timed

        animations = {EntityState.IDLE: {EntityDirection.RIGHT: animation}}
        super().__init__(animations, scale, has_direction=False, has_physics=False, level=level)

    def spawn(self) -> None:
        self.position = self.origin

        self.set_state(EntityState.DROPPING)
        self.movement_speed = config.constants.TRINKET_MOVEMENT_SPEED / 2.0

        angle = math.radians(random.uniform(0.0, 360.0))
        self.movement_vector = get_vector_from_angle(angle)

        scatter_delay = random.uniform(*config.constants.TRINKET_SCATTER_DELAY_RANGE)

        scene = get_gameplay_scene()
        scene.add_sprite('trinkets', self)

        def _pick_up() -> None:
            self.movement_speed = config.constants.TRINKET_MOVEMENT_SPEED
            self.set_state(EntityState.PICKED_UP)

        scene.add_timer(Timer(scatter_delay, callback=_pick_up))

    def apply_effect(self, player: Player) -> None:
        from noname_dungeon_crawler.assets import asset_repository

        arcade.play_sound(asset_repository.get_sound_effect('trinket_pickup'))
        if self.is_timed:
            get_gameplay_scene().add_timer(
                Timer(config.constants.TRINKET_DURATION, functools.partial(self.remove_effect, player))
            )

    def remove_effect(self, player: Player) -> None:
        raise NotImplementedError()

    def on_move(self, delta_time: float) -> None:
        if self.state == EntityState.PICKED_UP:
            player = get_player()
            angle = get_angle(self.position, player.position)
            self.movement_vector = get_vector_from_angle(angle)

    def on_player_collision(self, player: Player) -> None:  # type: ignore
        self.apply_effect(player)
        self.remove_from_sprite_lists()


class SpeedPotion(Trinket):
    def __init__(self, origin: arcade.Point, level: int) -> None:
        from noname_dungeon_crawler.assets import asset_repository

        animation = Animation(frames=[asset_repository.get_static_texture('flask_big_blue')], rate=1.0)
        super().__init__(origin, level, animation)

    def apply_effect(self, player: Player) -> None:
        player.movement_speed += config.constants.POTION_SPEED_INCREASE
        super().apply_effect(player)

    def remove_effect(self, player: Player) -> None:
        player.movement_speed -= config.constants.POTION_SPEED_INCREASE


class HealthPotion(Trinket):
    health_increase: float

    def __init__(self, origin: arcade.Point, level: int) -> None:
        from noname_dungeon_crawler.assets import asset_repository

        animation = Animation(frames=[asset_repository.get_static_texture('flask_big_red')], rate=1.0)
        super().__init__(origin, level, animation)

    def apply_effect(self, player: Player) -> None:
        self.health_increase = player.max_health * config.constants.POTION_HEALTH_INCREASE

        player.set_max_health(player.max_health + self.health_increase)
        super().apply_effect(player)

    def remove_effect(self, player: Player) -> None:
        player.set_max_health(player.max_health - self.health_increase)


class DamagePotion(Trinket):
    damage_increase: float

    def __init__(self, origin: arcade.Point, level: int) -> None:
        from noname_dungeon_crawler.assets import asset_repository

        animation = Animation(frames=[asset_repository.get_static_texture('flask_big_yellow')], rate=1.0)
        super().__init__(origin, level, animation)

    def apply_effect(self, player: Player) -> None:
        self.damage_increase = player.damage * config.constants.POTION_DAMAGE_INCREASE

        player.damage += self.damage_increase
        super().apply_effect(player)

    def remove_effect(self, player: Player) -> None:
        player.damage -= self.damage_increase


class HealingTrinket(Trinket):
    def __init__(self, origin: arcade.Point, level: int) -> None:
        from noname_dungeon_crawler.assets import asset_repository

        animation = Animation(frames=[asset_repository.get_static_texture('ui_heart_full')], rate=1.0)
        super().__init__(origin, level, animation, scale=0.2, is_timed=False)

    def apply_effect(self, player: Player) -> None:
        player.heal(self.level * 2)
        super().apply_effect(player)


class ExpTrinket(Trinket):
    damage_increase: float

    def __init__(self, origin: arcade.Point, level: int) -> None:
        from noname_dungeon_crawler.assets import asset_repository

        animation = Animation(frames=asset_repository.get_animated_texture('coin_anim'), rate=0.3)
        super().__init__(origin, level, animation, scale=0.2, is_timed=False)

    def apply_effect(self, player: Player) -> None:
        player.add_exp(self.level * 2)
        super().apply_effect(player)
