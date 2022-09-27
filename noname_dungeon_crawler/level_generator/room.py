import enum
import math
import random
import typing

import arcade

from noname_dungeon_crawler.settings import config
from noname_dungeon_crawler.sprites import Chest, Door, HostileMob
from noname_dungeon_crawler.util import get_scale


_FLOOR_TEXTURES = ('floor_1', 'floor_2', 'floor_3', 'floor_4', 'floor_5', 'floor_6', 'floor_7', 'floor_8')
_SPECIAL_WALL_TEXTURES = (
    'wall_hole_1',
    'wall_hole_2',
    'wall_goo',
    'wall_banner_red',
    'wall_banner_blue',
    'wall_banner_green',
    'wall_banner_yellow',
)


class RoomConnection(enum.Enum):
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3


class Room:
    """
    Генерация комнаты и наполнения комнаты
    """
    level: int

    size: int
    passage_size: int
    connections: typing.Set[RoomConnection]
    spawn_mobs: bool

    _floor_tiles: typing.List[typing.List[arcade.Sprite]]
    _additional_floor_tiles: typing.List[arcade.Sprite]

    _back_wall_tiles: typing.List[arcade.Sprite]
    _side_wall_tiles: typing.List[arcade.Sprite]

    chests: typing.List[Chest]
    mobs: typing.List[HostileMob]

    _scale: float

    def __init__(
        self,
        level: int,
        connections: typing.Set[RoomConnection] = set(),
        size: int = 9,
        passage_size: int = 3,
        spawn_mobs: bool = True,
    ) -> None:
        self.level = level
        self.size = size
        self.passage_size = passage_size
        self.connections = connections
        self.spawn_mobs = spawn_mobs

    def build(self) -> None:
        self._generate_floor()
        self._generate_walls()

    def shift(self, delta_x: float, delta_y: float) -> None:
        for tile_row in self._floor_tiles:
            for tile in tile_row:
                tile.center_x += delta_x
                tile.center_y += delta_y

        for tile in self._additional_floor_tiles:
            tile.center_x += delta_x
            tile.center_y += delta_y

        for tile in self._back_wall_tiles:
            tile.center_x += delta_x
            tile.center_y += delta_y

        for tile in self._side_wall_tiles:
            tile.center_x += delta_x
            tile.center_y += delta_y

    def make_entry(self) -> Door:
        self.spawn_mobs = False
        return self._generate_door(False)

    def make_exit(self) -> Door:
        return self._generate_door(True)

    def populate(self, hostile_mob_names: typing.List[str], max_mobs: int, max_chests: int) -> None:
        from noname_dungeon_crawler.assets import asset_repository

        self.chests = []
        self.mobs = []

        mob_type = random.choice(hostile_mob_names)
        spawn_chests = random.uniform(0, 1) <= config.constants.ROOM_CHEST_CHANCE

        populate_size = len(self._floor_tiles) - 2
        populate_cells = [(x + 1, y + 1) for x in range(populate_size) for y in range(populate_size)]
        num_populate = len(populate_cells)

        chests_spawned = 0
        mobs_spawned = 0

        if not self.spawn_mobs:
            max_mobs = 0

        for cell in populate_cells:
            if spawn_chests and chests_spawned < max_chests and random.uniform(0, 1) <= max_chests / num_populate:
                chest = Chest(level=self.level)
                chest.position = self._floor_tiles[cell[0]][cell[1]].position
                self.chests.append(chest)
                chests_spawned += 1
                continue

            if mobs_spawned < max_mobs and random.uniform(0, 1) <= max_mobs / num_populate:
                mob = typing.cast(HostileMob, asset_repository.get_entity(mob_type))
                mob.set_level(self.level)
                mob.position = self._floor_tiles[cell[0]][cell[1]].position
                self.mobs.append(mob)
                mobs_spawned += 1

    @property
    def floor_sprites(self) -> typing.List[arcade.Sprite]:
        flattened_tiles = [sprite for ax in self._floor_tiles for sprite in ax]
        flattened_tiles.extend(self._additional_floor_tiles)

        return flattened_tiles

    @property
    def wall_sprites(self) -> typing.List[arcade.Sprite]:
        return self._back_wall_tiles + self._side_wall_tiles

    @property
    def dim_px(self) -> float:
        return self.size * self._floor_tiles[0][0].width

    @property
    def center(self) -> arcade.Point:
        center_idx = math.floor(len(self._floor_tiles) / 2)
        return self._floor_tiles[center_idx][center_idx + 1].position

    def _generate_door(self, is_exit: bool) -> Door:
        door = Door(is_exit=is_exit, scale=1, level=self.level)  # type: ignore
        door.scale = get_scale(door.texture, config.constants.TILE_SCALE)

        target_tile = self._floor_tiles[self.size // 2][self.size - 1]
        door.position = (target_tile.center_x, target_tile.center_y + door.height)

        central_wall = self._back_wall_tiles[self.size + 3]  # A small hack for doors
        self._back_wall_tiles.remove(central_wall)

        return door

    def _generate_floor(self) -> None:
        from noname_dungeon_crawler.assets import asset_repository

        self._additional_floor_tiles = []

        tiles: typing.List[typing.List[typing.Optional[arcade.Sprite]]] = [
            [None for _y in range(self.size)] for _x in range(self.size)
        ]

        floor_textures = [asset_repository.get_static_texture(texture_name) for texture_name in _FLOOR_TEXTURES]
        self.scale = get_scale(floor_textures[0], config.constants.TILE_SCALE)

        for x in range(len(tiles)):
            for y in range(len(tiles[x])):
                texture_idx = random.randint(0, len(floor_textures) - 1)
                tiles[x][y] = arcade.Sprite(texture=floor_textures[texture_idx], scale=self.scale)

        tiles = typing.cast(typing.List[typing.List[arcade.Sprite]], tiles)

        tile_size = tiles[0][0].width

        for x in range(len(tiles)):
            for y in range(len(tiles[x])):
                tiles[x][y].center_x = x * tile_size
                tiles[x][y].center_y = y * tile_size

        self._floor_tiles = tiles

        if RoomConnection.TOP in self.connections:
            for tile_idx in range(*self._passage_idx_range):
                texture_idx = random.randint(0, len(floor_textures) - 1)
                tile = arcade.Sprite(texture=floor_textures[texture_idx], scale=self.scale)
                tile.set_position(
                    center_x=self._floor_tiles[tile_idx - 1][self.size - 1].center_x + tile_size,
                    center_y=self._floor_tiles[tile_idx - 1][self.size - 1].center_y + tile_size,
                )
                self._additional_floor_tiles.append(tile)

    def _generate_walls(self) -> None:
        self._back_wall_tiles = []
        self._side_wall_tiles = []

        self._generate_back_wall()
        self._generate_side_walls()

    def _generate_back_wall(self) -> None:
        from noname_dungeon_crawler.assets import asset_repository

        max_tile_idx = self.size - 1
        tile_size = self._floor_tiles[0][0].width

        back_walls: typing.List[arcade.Sprite] = []

        back_wall_texture_left = (
            asset_repository.get_static_texture('wall_mid')
            if RoomConnection.LEFT in self.connections
            else asset_repository.get_static_texture('wall_corner_left')
        )
        back_wall_texture_mid = asset_repository.get_static_texture('wall_mid')
        back_wall_texture_right = asset_repository.get_static_texture('wall_corner_right')

        back_wall_left = arcade.Sprite(texture=back_wall_texture_left, scale=self.scale)
        back_wall_left.set_position(
            self._floor_tiles[0][max_tile_idx].center_x, self._floor_tiles[0][max_tile_idx].center_y + tile_size
        )
        top_left_corner = arcade.Sprite(
            texture=asset_repository.get_static_texture('wall_corner_top_left'), scale=self.scale
        )
        top_left_corner.set_position(back_wall_left.center_x, back_wall_left.center_y + tile_size)
        back_walls.extend((back_wall_left, top_left_corner))

        back_wall_right = arcade.Sprite(texture=back_wall_texture_right, scale=self.scale)
        back_wall_right.set_position(
            self._floor_tiles[max_tile_idx][max_tile_idx].center_x,
            self._floor_tiles[max_tile_idx][max_tile_idx].center_y + tile_size,
        )
        top_right_corner = arcade.Sprite(
            texture=asset_repository.get_static_texture('wall_corner_top_right'), scale=self.scale
        )
        top_right_corner.set_position(
            back_wall_right.center_x,
            back_wall_right.center_y + tile_size,
        )
        back_walls.extend((back_wall_right, top_right_corner))

        for wall_idx in range(0, max_tile_idx):
            if RoomConnection.TOP in self.connections and wall_idx in range(*self._passage_idx_range):
                continue

            texture = (
                asset_repository.get_static_texture(random.choice(_SPECIAL_WALL_TEXTURES))
                if random.uniform(0, 1) <= 0.35
                else back_wall_texture_mid
            )

            back_wall_mid = arcade.Sprite(texture=texture, scale=self.scale)
            back_wall_mid.set_position(
                self._floor_tiles[wall_idx][max_tile_idx].center_x,
                self._floor_tiles[wall_idx][max_tile_idx].center_y + tile_size,
            )
            back_walls.append(back_wall_mid)
            top_mid_wall = arcade.Sprite(texture=asset_repository.get_static_texture('wall_top_mid'), scale=self.scale)
            top_mid_wall.set_position(
                back_wall_mid.center_x,
                back_wall_mid.center_y + tile_size,
            )
            back_walls.append(top_mid_wall)

        self._back_wall_tiles.extend(back_walls)

    def _generate_side_walls(self) -> None:
        from noname_dungeon_crawler.assets import asset_repository

        max_tile_idx = self.size - 1

        # Bottom wall
        if RoomConnection.BOTTOM not in self.connections:
            max_tile_idx = self.size - 1

            bottom_walls: typing.List[arcade.Sprite] = []
            for wall_idx in range(0, max_tile_idx + 1):
                wall = arcade.Sprite(texture=asset_repository.get_static_texture('wall_top_mid'), scale=self.scale)
                wall.set_position(self._floor_tiles[wall_idx][0].center_x, self._floor_tiles[wall_idx][0].center_y)
                bottom_walls.append(wall)

            self._side_wall_tiles.extend(bottom_walls)

        # Right wall
        right_walls: typing.List[arcade.Sprite] = []
        for wall_idx in range(0, max_tile_idx + 1):
            if RoomConnection.RIGHT in self.connections and wall_idx in range(*self._passage_idx_range):
                continue

            wall = arcade.Sprite(texture=asset_repository.get_static_texture('wall_side_mid_left'), scale=self.scale)
            wall.set_position(
                self._floor_tiles[max_tile_idx][wall_idx].center_x, self._floor_tiles[max_tile_idx][wall_idx].center_y
            )
            right_walls.append(wall)
        self._side_wall_tiles.extend(right_walls)

        # Left wall
        if RoomConnection.LEFT not in self.connections:
            left_walls: typing.List[arcade.Sprite] = []
            for wall_idx in range(0, max_tile_idx + 1):
                wall = arcade.Sprite(
                    texture=asset_repository.get_static_texture('wall_side_mid_right'), scale=self.scale
                )
                wall.set_position(self._floor_tiles[0][wall_idx].center_x, self._floor_tiles[0][wall_idx].center_y)
                left_walls.append(wall)
            self._side_wall_tiles.extend(left_walls)

    @property
    def _passage_idx_range(self) -> typing.Tuple[int, int]:
        start_idx = math.floor((self.size - self.passage_size) / 2)
        return start_idx, start_idx + self.passage_size
