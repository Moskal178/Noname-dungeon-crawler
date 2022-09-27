import typing

import arcade


def draw_bar_with_text(
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    inner_color: typing.Tuple[int, int, int],
    inner_filled: float,
    outline_thickness: float,
    text: str,
) -> None:
    arcade.draw_rectangle_filled(
        center_x, center_y, width + outline_thickness * 2, height + outline_thickness * 2, arcade.color.BLACK
    )
    arcade.draw_rectangle_outline(
        center_x,
        center_y,
        width + outline_thickness * 2,
        height + outline_thickness * 2,
        color=arcade.color.WHITE,
        border_width=outline_thickness,
    )

    inner_width = width * inner_filled
    inner_center_x = center_x - ((width - inner_width) / 2)

    arcade.draw_rectangle_filled(inner_center_x, center_y, inner_width, height, inner_color)
    arcade.draw_text(
        text,
        start_x=center_x,
        start_y=center_y * 1.005,
        color=arcade.color.WHITE,
        font_size=height / 2,
        anchor_x='center',
        anchor_y='center',
    )
