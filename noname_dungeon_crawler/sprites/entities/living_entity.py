import math
import typing

import arcade

from noname_dungeon_crawler.sprites import Animation
from noname_dungeon_crawler.settings import config
from noname_dungeon_crawler.util import Timer, get_angle, get_gameplay_scene, pts_to_px

from .entity import MovingEntity
from .entity_states import EntityDirection, EntityState


class LivingEntity(MovingEntity):
    max_health: float
    _health: float
    damage: float

    behavior_meta: typing.Dict[str, typing.Any]
    sounds: typing.Dict[str, arcade.Sound]

    def __init__(
        self,
        max_health: float,
        damage: float,
        movement_speed: float,
        animations: typing.Dict[EntityState, typing.Dict[EntityDirection, Animation]],
        scale: float,
        sounds: typing.Dict[str, arcade.Sound] = {},
        level: int = 1,
    ) -> None:
        super().__init__(animations, scale, level=level)

        self.max_health = max_health
        self._health = self.max_health

        self.movement_speed = movement_speed
        self.movement_vector = [0, 0]

        self.damage = damage

        self.behavior_meta = {}
        self.sounds = sounds

    def heal(self, health: float) -> None:
        self._health = min(self._health + health, self.max_health)

    def take_damage(self, attacker: 'LivingEntity') -> None:
        if self.state in (EntityState.ATTACKED, EntityState.DYING):
            return

        self._health -= attacker.damage

        angle = get_angle(attacker.position, self.position)
        self.change_x = math.cos(angle) * self.width * 0.05
        self.change_y = math.sin(angle) * self.height * 0.05

        if self._health <= 0:
            self.die(attacker)
            return

        previous_state = self.state
        previous_color = self.color

        def _restore_state() -> None:
            self.set_state(previous_state)
            self.color = previous_color

            self.change_x = 0
            self.change_y = 0

        if 'hurt' in self.sounds:
            arcade.play_sound(self.sounds['hurt'], volume=config.music_volume)

        self.set_state(EntityState.ATTACKED, animation_key=EntityState.IDLE)
        self.color = (255, 0, 0)

        get_gameplay_scene().add_timer(Timer(config.constants.DAMAGE_TTL, callback=_restore_state))

    def set_max_health(self, new_health: float) -> None:
        factor = new_health / self.max_health
        self.max_health = new_health
        self._health = math.ceil(self._health * factor)

    def die(self, attacker: 'LivingEntity') -> None:
        self.on_death(attacker)

        if 'death' in self.sounds:
            arcade.play_sound(self.sounds['death'], volume=config.music_volume)

        self.set_state(EntityState.DYING, animation_key=EntityState.IDLE)
        self.color = (255, 0, 0)

        get_gameplay_scene().add_timer(Timer(config.constants.DEATH_TTL, callback=self.remove_from_sprite_lists))

    def on_update(self, delta_time: float = 1 / 60) -> None:
        match self.state:
            case EntityState.IDLE | EntityState.MOVING:
                self._move(delta_time)
            case EntityState.DYING:
                self._die(delta_time)

    def get_copy(self) -> 'LivingEntity':
        return self.__class__(
            max_health=self.max_health,
            damage=self.damage,
            movement_speed=self.movement_speed,
            animations=self.animations,
            scale=self.sprite_scale,
            sounds=self.sounds,
        )

    def _die(self, delta_time: float) -> None:
        angle = 90 * delta_time / (config.constants.DEATH_TTL * config.constants.SCALE)
        self.turn_right(angle)

    def draw_hp_bar(self) -> None:
        if self.state != EntityState.ATTACKED:
            return

        width = self.width
        height = pts_to_px(config.constants.HP_BAR_HEIGHT)

        health_missing = 1.0 - (max(self._health, 0.0) / self.max_health)

        arcade.draw_rectangle_filled(
            self.center_x,
            self.top + height * 3,
            width=width,
            height=height,
            color=arcade.color.GREEN,
        )
        arcade.draw_rectangle_filled(
            self.center_x,
            self.top + height * 3,
            width=width * health_missing,
            height=height,
            color=arcade.color.RED,
        )

    def set_level(self, level: int) -> None:
        self.level = level
        self.scale_stats()

    def scale_stats(self) -> None:
        raise NotImplementedError()

    def on_death(self, attacker: 'LivingEntity') -> None:
        pass

    @classmethod
    def args_from_config(cls, entity_config: dict) -> typing.Tuple[str, dict]:
        from noname_dungeon_crawler.assets import asset_repository

        name, args = super().args_from_config(entity_config)

        args['max_health'] = entity_config['stats']['health']
        args['damage'] = entity_config['stats']['damage']
        args['movement_speed'] = entity_config['stats']['movement_speed']

        if 'sounds' in entity_config:
            args['sounds'] = {
                sound_trigger: asset_repository.get_sound_effect(sound_name)
                for sound_trigger, sound_name in entity_config['sounds'].items()
            }

        return name, args
