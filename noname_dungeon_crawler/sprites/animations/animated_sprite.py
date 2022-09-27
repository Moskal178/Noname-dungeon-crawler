import typing

import arcade
import attr

from ..scaled_sprite import ScaledSprite


@attr.s(kw_only=True, auto_attribs=True)
class Animation:
    frames: typing.List[arcade.Texture]
    rate: float  # in seconds
    since_last_frame: float = 0  # in seconds

    _current_texture: int = 0

    def get_next_texture(self) -> arcade.Texture:
        self.since_last_frame = 0
        self._current_texture = self._current_texture + 1 if self._current_texture < len(self.frames) - 1 else 0
        return self.frames[self._current_texture]


class AnimatedSprite(ScaledSprite):
    animation: Animation

    def __init__(
        self,
        animation: Animation,
        scale: float = 1.0,
        **kwargs: typing.Any,
    ) -> None:
        self.animation = animation
        initial_texture = self.animation.frames[0]
        super().__init__(**kwargs, texture=initial_texture, scale=scale)

    def set_animation(self, animation: Animation) -> None:
        animation.since_last_frame = 0
        animation._current_texture = 0

        self.animation = animation

    def update_animation(self, delta_time: float = 1 / 60) -> None:
        self.animation.since_last_frame += delta_time

        if self.animation.since_last_frame >= self.animation.rate:
            self.texture = self.animation.get_next_texture()
