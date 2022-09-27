import logging
import pathlib
import typing

import attr


__all__ = ['config']


class Constants:
    ASSETS_BASE_DIR = pathlib.Path(__file__).parent.parent / 'assets'
    ENTITY_DIR = ASSETS_BASE_DIR / 'entities'
    TEXTURE_DIR = ASSETS_BASE_DIR / 'textures'
    IMAGE_DIR = ASSETS_BASE_DIR / 'images'
    SOUND_DIR = ASSETS_BASE_DIR / 'sounds'

    PLAYER_BASE_HEALTH = 20
    PLAYER_BASE_DAMAGE = 5

    PLAYER_WEAPON_SWING_SPEED = 1.5
    ATTACK_TTL = 0.2
    DAMAGE_TTL = 0.12
    DEATH_TTL = 0.5
    HP_BAR_HEIGHT = 0.03

    SCALE = 2

    MISC_OBJECT_COLLISION_CHECK_INTERVAL = 0.5

    TRINKET_MOVEMENT_SPEED = 5.0
    TRINKET_SCATTER_DELAY_RANGE = (0.1, 0.3)
    TRINKET_DURATION = 30.0

    MOB_HEALING_DROP_CHANCE = 0.3

    POTION_SPEED_INCREASE = 0.8
    POTION_HEALTH_INCREASE = 0.3
    POTION_DAMAGE_INCREASE = 0.3

    TILE_SCALE = 0.35

    GENERATOR_GRID_SIZE = 25
    GENERATOR_ROOM_SIZE = 9
    GENERATOR_PASSAGE_SIZE = 3
    GENERATOR_PROBABILITY_DECAY = 0.7
    GENERATOR_MAX_MOBS = 5
    GENERATOR_MAX_CHESTS = 1

    ROOM_CHEST_CHANCE = 0.3

    LOGGING_CONFIG = {
        'level': logging.INFO,
        'format': '[%(asctime)s] %(levelname)s: %(processName)s<%(name)s> %(message)s',
    }


@attr.s(kw_only=True, auto_attribs=True)
class _GameConfig:
    resolution: typing.Tuple[int, int] = (1920, 1080)
    music_volume: float = 0.2

    constants: Constants = Constants()


config = _GameConfig()
