import math
import typing

import arcade

from noname_dungeon_crawler.settings import config


if typing.TYPE_CHECKING:
    from sprites import Player

    from .game import NonameDungeonCrawler
    from .scenes import GameplayScene


class Timer:
    duration: float
    callback: typing.Callable[[], None]

    _elapsed: float

    def __init__(self, duration: float, callback: typing.Callable[[], None]) -> None:
        self.duration = duration
        self.callback = callback  # type: ignore

        self._elapsed = 0

    def update(self, delta_time: float) -> None:
        self._elapsed += delta_time

        if self.finished:
            self.callback()  # type: ignore

    @property
    def finished(self) -> bool:
        return self._elapsed >= self.duration


def pts_to_px(pts: float) -> float:
    """
    Конвертр пикселей в условные единицы расстояний
    """
    return config.resolution[0] / 10.0 * pts * config.constants.SCALE


def get_scale(texture: arcade.Texture, scale: float) -> float:
    target_w = pts_to_px(scale)
    return target_w / texture.width


def get_angle(
    source_point: arcade.Point,
    target_point: arcade.Point,
) -> float:
    """
    Угол между точками
    """
    diff_x = target_point[0] - source_point[0]
    diff_y = target_point[1] - source_point[1]

    return math.atan2(diff_y, diff_x)


def get_vector_from_angle(angle: float) -> typing.List[float]:
    return [math.cos(angle), math.sin(angle)]


def point_in_eps(
    source_point: typing.Tuple[float, float], target_point: typing.Tuple[float, float], eps: float
) -> bool:
    """
    Находится ли точка в расстоянии от другой точки
    """
    return abs(source_point[0] - target_point[0]) <= eps and abs(source_point[1] - target_point[1]) <= eps


def get_game() -> 'NonameDungeonCrawler':
    from .game import NonameDungeonCrawler

    return NonameDungeonCrawler.get_instance()


def get_gameplay_scene() -> 'GameplayScene':
    return get_game().get_gameplay_scene()


def get_player() -> 'Player':
    return get_gameplay_scene().player_entity
