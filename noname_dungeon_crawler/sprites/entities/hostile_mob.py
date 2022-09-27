import functools
import random
import typing

import arcade

from noname_dungeon_crawler.settings import config
from noname_dungeon_crawler.util import Timer, get_gameplay_scene, get_player, point_in_eps, pts_to_px

from .entity_states import EntityState
from .living_entity import LivingEntity
from .trinkets import ExpTrinket, HealingTrinket


if typing.TYPE_CHECKING:
    from .player import Player


_PATHFINDING_RANGE = 3


class HostileMob(LivingEntity):
    def on_move(self, delta_time: float) -> None:
        player = get_player()

        source = typing.cast(typing.Tuple[float, float], self.position)
        target = typing.cast(typing.Tuple[float, float], player.position)

        # Cancel pathfinding when not in range
        if not point_in_eps(source, target, pts_to_px(_PATHFINDING_RANGE)):
            self.movement_vector = [0, 0]
            return

        self.movement_vector = [target[0] - source[0], target[1] - source[1]]

    def on_player_collision(self, player: 'Player') -> None:
        self.set_state(EntityState.ATTACKING, animation_key=EntityState.IDLE)
        self.change_x = 0
        self.change_y = 0

        get_gameplay_scene().add_timer(
            Timer(config.constants.ATTACK_TTL, functools.partial(self.set_state, EntityState.IDLE))
        )

        if 'attack' in self.sounds:
            arcade.play_sound(self.sounds['attack'], volume=config.music_volume)

        player.take_damage(self)

    def on_death(self, attacker: 'LivingEntity') -> None:
        ExpTrinket(self.position, self.level).spawn()

        if random.uniform(0, 1) <= config.constants.MOB_HEALING_DROP_CHANCE:
            HealingTrinket(self.position, self.level).spawn()

    def scale_stats(self) -> None:
        self.max_health *= self.level
        self.damage *= self.level
