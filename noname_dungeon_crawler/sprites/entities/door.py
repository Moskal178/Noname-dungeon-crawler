import arcade

from noname_dungeon_crawler.sprites import Animation
from noname_dungeon_crawler.util import Timer, get_gameplay_scene

from .entity import Entity
from .entity_states import EntityDirection, EntityState


class Door(Entity):
    is_exit: bool

    def __init__(self, is_exit: bool, scale: float, level: int) -> None:
        from noname_dungeon_crawler.assets import asset_repository

        self.is_exit = is_exit

        animations = {
            EntityState.IDLE: {
                EntityDirection.RIGHT: Animation(
                    frames=[asset_repository.get_static_texture('doors_leaf_closed')], rate=1.0
                )
            },
            EntityState.OPENED: {
                EntityDirection.RIGHT: Animation(
                    frames=[asset_repository.get_static_texture('doors_leaf_open')], rate=1.0
                )
            },
        }

        super().__init__(animations, scale, level)

    def open(self) -> None:
        from noname_dungeon_crawler.assets import asset_repository

        if self.state == EntityState.OPENED:
            return

        if not self.is_exit:
            return

        scene = get_gameplay_scene()

        arcade.play_sound(asset_repository.get_sound_effect('door_open'))
        self.set_state(EntityState.OPENED)
        scene.add_timer(Timer(duration=0.6, callback=scene.start_next_level))
