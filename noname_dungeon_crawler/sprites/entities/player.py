import functools
import math
import typing

import arcade

from noname_dungeon_crawler.settings import config
from noname_dungeon_crawler.util import Timer, get_angle, get_game, get_gameplay_scene, pts_to_px

from .door import Door
from .entity_states import EntityState
from .living_entity import LivingEntity

from ..scaled_sprite import ScaledSprite


class PlayerWeapon(ScaledSprite):
    player: LivingEntity
    attack_angle: float

    _since_created: float
    _hit_enemies: typing.Set[arcade.Sprite]

    def __init__(
        self,
        player: LivingEntity,
        target_point: typing.Tuple[float, float],
        enemies: arcade.SpriteList,
        chests: arcade.SpriteList,
        doors: arcade.SpriteList,
        **kwargs: typing.Any,
    ) -> None:
        from noname_dungeon_crawler.assets import asset_repository

        self.player = player
        self.enemies = enemies
        self.chests = chests
        self.doors = doors

        self._since_created = 0
        self._hit_enemies = set()

        texture = asset_repository.get_static_texture('weapon_regular_sword')
        scale = 0.25

        self.attack_angle = get_angle(typing.cast(typing.Tuple[float, float], player.position), target_point)
        center_x = player.center_x + math.cos(self.attack_angle) * scale
        center_y = player.center_y + math.sin(self.attack_angle) * scale

        super().__init__(
            **kwargs,
            texture=texture,
            scale=scale,
            angle=math.degrees(self.attack_angle) - 90,
            center_x=center_x,
            center_y=center_y,
        )

    def on_update(self, delta_time: float = 1 / 60) -> None:
        from .chest import Chest

        if self._since_created >= config.constants.ATTACK_TTL:
            self.remove_from_sprite_lists()

        speed = pts_to_px(config.constants.PLAYER_WEAPON_SWING_SPEED)

        self.center_x = self.player.center_x + math.cos(self.attack_angle) * (
            (self._since_created * speed) + self.player.width / 3
        )
        self.center_y = self.player.center_y + math.sin(self.attack_angle) * (
            (self._since_created * speed) + self.player.height / 3
        )

        self._since_created += delta_time

        for enemy in arcade.check_for_collision_with_list(self, self.enemies):
            enemy = typing.cast(LivingEntity, enemy)

            if enemy in self._hit_enemies:
                continue
            self._hit_enemies.add(enemy)

            enemy.take_damage(self.player)

        for chest in arcade.check_for_collision_with_list(self, self.chests):
            chest = typing.cast(Chest, chest)

            if chest.state == EntityState.IDLE:
                chest.unlock()

        for door in arcade.check_for_collision_with_list(self, self.doors):
            door = typing.cast(Door, door)
            door.open()


class Player(LivingEntity):
    current_exp: int
    exp_to_next_level: int

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)

        self.current_exp = 0
        self.set_level(1)

    def swing_weapon(self, x: float, y: float) -> None:
        from noname_dungeon_crawler.assets import asset_repository

        if not self.behavior_meta.get('attacking') and self.state not in (EntityState.ATTACKED, EntityState.DYING):
            scene = get_gameplay_scene()

            arcade.play_sound(asset_repository.get_sound_effect('player_weapon_swing'), volume=config.music_volume)

            scene.add_sprite(
                'weapon',
                PlayerWeapon(
                    self,
                    (x, y),
                    scene.get_sprite_list('mobs'),
                    scene.get_sprite_list('chests'),
                    scene.get_sprite_list('doors'),
                ),
            )
            self.behavior_meta['attacking'] = True

            def _reset_attack_stance() -> None:
                self.behavior_meta['attacking'] = False

            scene.add_timer(Timer(config.constants.ATTACK_TTL, callback=_reset_attack_stance))  # type: ignore

    def add_exp(self, exp: int) -> None:
        from noname_dungeon_crawler.assets import asset_repository

        self.current_exp += exp
        if self.current_exp >= self.exp_to_next_level:
            arcade.play_sound(asset_repository.get_sound_effect('player_levelup'), volume=config.music_volume)

            self.current_exp -= self.exp_to_next_level
            self.set_level(self.level + 1)

    def scale_stats(self) -> None:
        self.set_max_health(config.constants.PLAYER_BASE_HEALTH * (1 + self.level * 0.5))
        self.damage = config.constants.PLAYER_BASE_DAMAGE * (1 + self.level * 0.5)

        self.exp_to_next_level = 4 * self.level ** 2 + 8 * self.level + 20

    def on_death(self, attacker: 'LivingEntity') -> None:
        from noname_dungeon_crawler.scenes import SceneType

        game = get_game()
        get_gameplay_scene().add_timer(
            Timer(duration=1.5, callback=functools.partial(game.activate_scene, SceneType.MAIN_MENU, True))
        )
