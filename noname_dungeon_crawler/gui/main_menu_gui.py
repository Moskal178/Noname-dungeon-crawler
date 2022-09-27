import arcade.gui

from noname_dungeon_crawler.settings import config
from noname_dungeon_crawler.util import get_game, pts_to_px


def _start_click(event: arcade.gui.UIEvent) -> None:
    from noname_dungeon_crawler.scenes import SceneType

    get_game().activate_scene(SceneType.GAMEPLAY, clear=True)


def get_main_menu_gui() -> arcade.gui.UIManager:
    manager = arcade.gui.UIManager()

    screen_center_x = config.resolution[0] // 2
    screen_center_y = config.resolution[1] // 2

    button_width = pts_to_px(1)
    button_height = pts_to_px(0.3)

    start_button = arcade.gui.UIFlatButton(
        text="Start",
        x=screen_center_x - button_width // 2,
        y=screen_center_y - button_height // 2,
        width=button_width,
        height=button_height,
    )
    start_button.on_click = _start_click  # type: ignore
    manager.add(start_button)

    exit_button = arcade.gui.UIFlatButton(
        text="Exit",
        x=screen_center_x - button_width // 2,
        y=screen_center_y - pts_to_px(0.6) - button_height // 2,
        width=button_width,
        height=button_height,
    )
    exit_button.on_click = exit  # type: ignore
    manager.add(exit_button)

    return manager
