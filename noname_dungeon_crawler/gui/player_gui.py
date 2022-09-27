import arcade

from noname_dungeon_crawler.sprites import Player
from noname_dungeon_crawler.util import pts_to_px

from .drawing import draw_bar_with_text


def draw_player_gui(player: Player) -> None:
    hp_bar_center = (pts_to_px(0.6), pts_to_px(2.65))

    draw_bar_with_text(  # HP bar
        center_x=hp_bar_center[0],
        center_y=hp_bar_center[1],
        width=pts_to_px(1),
        height=pts_to_px(0.1),
        inner_color=arcade.color.DARK_RED,
        inner_filled=player._health / player.max_health,
        outline_thickness=pts_to_px(0.01),
        text=f'{int(player._health)}/{int(player.max_health)}',
    )

    draw_bar_with_text(  # EXP bar
        center_x=hp_bar_center[0],
        center_y=hp_bar_center[1] - pts_to_px(0.15),
        width=pts_to_px(1),
        height=pts_to_px(0.1),
        inner_color=arcade.color.DARK_GREEN,
        inner_filled=player.current_exp / player.exp_to_next_level,
        outline_thickness=pts_to_px(0.01),
        text=f'Lv. {player.level} ({int(player.current_exp)}/{int(player.exp_to_next_level)})',
    )
