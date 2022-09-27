import collections
import math
import typing

import arcade

from noname_dungeon_crawler.sprites import Animation, AnimatedSprite
from noname_dungeon_crawler.util import get_gameplay_scene, get_player, pts_to_px

from .entity_states import EntityDirection, EntityState


if typing.TYPE_CHECKING:
    from .player import Player


import logging

log = logging.getLogger(__name__)


class Entity(AnimatedSprite):
    sprite_scale: float
    animations: typing.Dict[EntityState, typing.Dict[EntityDirection, Animation]]

    direction: EntityDirection
    state: EntityState

    level: int

    def __init__(
        self,
        animations: typing.Dict[EntityState, typing.Dict[EntityDirection, Animation]],
        scale: float,
        level: int = 1,
    ) -> None:
        self.sprite_scale = scale
        self.animations = animations

        self.direction = EntityDirection.RIGHT
        self.state = EntityState.IDLE

        self.level = level

        initial_animation = self.animations[self.state][self.direction]

        super().__init__(animation=initial_animation, scale=self.sprite_scale)

    def set_direction(self, direction: EntityDirection) -> None:
        if self.direction == direction:
            return

        self.direction = direction
        self.set_animation(self.animations[self.state][direction])

    def set_state(self, state: EntityState, animation_key: typing.Optional[EntityState] = None) -> None:
        if self.state == state:
            return

        self.state = state

        anim_key = animation_key or state
        if anim_key not in self.animations:
            anim_key = EntityState.IDLE

        self.set_animation(self.animations[anim_key][self.direction])

    def get_copy(self) -> 'Entity':
        return self.__class__(animations=self.animations, scale=self.sprite_scale)

    @classmethod
    def args_from_config(cls, entity_config: dict) -> typing.Tuple[str, dict]:
        from noname_dungeon_crawler.assets import asset_repository

        animations: typing.Dict[EntityState, typing.Dict[EntityDirection, Animation]] = collections.defaultdict(dict)

        for animation_config in entity_config['animations']:
            animations[EntityState[animation_config['state']]][EntityDirection.RIGHT] = Animation(
                frames=asset_repository.get_animated_texture(animation_config['name']),
                rate=animation_config['rate'],
            )

            try:  # Also try to load flipped texture (if exists)
                animations[EntityState[animation_config['state']]][EntityDirection.LEFT] = Animation(
                    frames=asset_repository.get_animated_texture(f"{animation_config['name']}_flipped"),
                    rate=animation_config['rate'],
                )
            except KeyError:
                pass

        return entity_config['name'], {'animations': dict(animations), 'scale': entity_config['sprite_scale']}


class MovingEntity(Entity):
    movement_speed: float  # pts / second
    movement_vector: typing.List[float]

    has_direction: bool
    has_physics: bool

    physics_engine: typing.Optional[arcade.PhysicsEngineSimple]

    def __init__(
        self,
        animations: typing.Dict[EntityState, typing.Dict[EntityDirection, Animation]],
        scale: float,
        has_direction: bool = True,
        has_physics: bool = True,
        level: int = 1,
    ) -> None:
        self.has_direction = has_direction
        self.has_physics = has_physics

        super().__init__(animations, scale, level=level)

    def on_update(self, delta_time: float = 1 / 60) -> None:
        self._move(delta_time)

    def _move(self, delta_time: float) -> None:
        self.on_move(delta_time)

        if self.movement_vector == [0, 0]:
            self.set_state(EntityState.IDLE)
            self.change_x = 0
            self.change_y = 0
            return

        angle = math.atan2(self.movement_vector[1], self.movement_vector[0])

        if self.state == EntityState.IDLE:
            self.set_state(EntityState.MOVING)

        if self.has_direction:
            self.set_direction(EntityDirection.RIGHT if abs(angle) < 1.6 else EntityDirection.LEFT)

        speed = pts_to_px(self.movement_speed) * delta_time

        if self.has_physics:
            self.change_x = math.cos(angle) * speed
            self.change_y = math.sin(angle) * speed
        else:
            self.center_x += math.cos(angle) * speed
            self.center_y += math.sin(angle) * speed

        player = get_player()
        collision = arcade.check_for_collision(self, player)

        if collision:
            self.on_player_collision(player)

    def remove_from_sprite_lists(self) -> None:
        if self.has_physics:
            get_gameplay_scene().remove_physics_engine(self)

        super().remove_from_sprite_lists()

    def on_move(self, delta_time: float) -> None:
        pass

    def on_player_collision(self, player: 'Player') -> None:
        pass
