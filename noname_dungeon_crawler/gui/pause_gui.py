import arcade.gui

from noname_dungeon_crawler.settings import config
from noname_dungeon_crawler.util import get_game, pts_to_px


def _resume_click(event: arcade.gui.UIEvent) -> None:
    get_game().deactivate_scene()


def _exit_click(event: arcade.gui.UIEvent) -> None:
    from noname_dungeon_crawler.scenes import SceneType

    get_game().activate_scene(SceneType.MAIN_MENU, clear=True)


def get_pause_gui() -> arcade.gui.UIManager:
    manager = arcade.gui.UIManager()

    screen_center_x = config.resolution[0] // 2
    screen_center_y = config.resolution[1] // 2

    button_width = pts_to_px(1)
    button_height = pts_to_px(0.3)

    resume_button = arcade.gui.UIFlatButton(
        text="Resume",
        x=screen_center_x - button_width // 2,
        y=screen_center_y + pts_to_px(0.3) - button_height // 2,
        width=button_width,
        height=button_height,
    )
    resume_button.on_click = _resume_click  # type: ignore
    manager.add(resume_button)

    exit_button = arcade.gui.UIFlatButton(
        text="Exit",
        x=screen_center_x - button_width // 2,
        y=screen_center_y - pts_to_px(0.3) - button_height // 2,
        width=button_width,
        height=button_height,
    )
    exit_button.on_click = _exit_click  # type: ignore
    manager.add(exit_button)

    return manager
