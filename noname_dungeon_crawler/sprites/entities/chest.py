import random

import arcade

from noname_dungeon_crawler.sprites import Animation
from noname_dungeon_crawler.util import Timer, get_gameplay_scene

from .entity import Entity
from .entity_states import EntityDirection, EntityState
from .trinkets import ExpTrinket, DamagePotion, HealthPotion, SpeedPotion


class Chest(Entity):
    _TRINKETS = (ExpTrinket, DamagePotion, HealthPotion, SpeedPotion)

    def __init__(self, level: int) -> None:
        from noname_dungeon_crawler.assets import asset_repository

        animations = {
            EntityState.IDLE: {
                EntityDirection.RIGHT: Animation(
                    frames=[asset_repository.get_animated_texture('chest_full_open_anim')[0]], rate=1.0
                )
            },
            EntityState.OPENING: {
                EntityDirection.RIGHT: Animation(
                    frames=asset_repository.get_animated_texture('chest_full_open_anim'), rate=0.2
                )
            },
            EntityState.OPENED: {
                EntityDirection.RIGHT: Animation(
                    frames=[asset_repository.get_animated_texture('chest_full_open_anim')[-1]], rate=1.0
                )
            },
        }

        super().__init__(animations, 0.3, level=level)

    def unlock(self) -> None:
        from noname_dungeon_crawler.assets import asset_repository

        arcade.play_sound(asset_repository.get_sound_effect('chest_open'))
        self.set_state(EntityState.OPENING)

        open_anim = self.animations[EntityState.OPENING][EntityDirection.RIGHT]
        open_duration = open_anim.rate * len(open_anim.frames)

        get_gameplay_scene().add_timer(Timer(open_duration, self.deposit_loot))

    def deposit_loot(self) -> None:
        TrinketType = random.choice(self._TRINKETS)

        self.set_state(EntityState.OPENED)
        TrinketType(self.position, self.level).spawn()
