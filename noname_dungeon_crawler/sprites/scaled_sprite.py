import typing

import arcade

from noname_dungeon_crawler.util import get_scale


class ScaledSprite(arcade.Sprite):
    scale_factor: float

    def __init__(self, scale: float, texture: arcade.Texture, **kwargs: typing.Any) -> None:
        self.scale_factor = get_scale(texture, scale)
        super().__init__(**kwargs, texture=texture, scale=self.scale_factor)
