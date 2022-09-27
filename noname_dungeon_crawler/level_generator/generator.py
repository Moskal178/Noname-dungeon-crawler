import math
import random
import typing

import arcade
import attr

from noname_dungeon_crawler.settings import config
from noname_dungeon_crawler.sprites import HostileMob

from .room import Room, RoomConnection


@attr.s(kw_only=True, auto_attribs=True)
class _LevelDump:
    """
    Класс для хранения данных после преобразования в спрайты
    """
    floor: arcade.SpriteList
    walls: arcade.SpriteList
    mobs: arcade.SpriteList
    chests: arcade.SpriteList
    doors: arcade.SpriteList

    starting_coords: arcade.Point


class LevelGenerator:
    """
    1. Генерация матрицы 25 на 25
    2. В центре создается комната
    3. Генерируется по 1 комнате в 4 сторонах от центральной с шансом 100%
    4. Рекурсивная генерация комнат с уменьшением вероятности генерации с каждой новой комнатой
    5. Рекурсия заканчивается или при вероятности=0, или при окончании заданной матрицы
    """
    level: int

    grid: typing.List[typing.List[typing.Optional[Room]]]
    starting_coords: arcade.Point

    _doors: arcade.SpriteList

    def __init__(self, level: int) -> None:
        self.level = level

        grid_size = config.constants.GENERATOR_GRID_SIZE
        self.grid = [[None for _y in range(grid_size)] for _x in range(grid_size)]

    def generate_level(self) -> _LevelDump:
        center_idx = math.floor(len(self.grid) / 2)
        self.grid[center_idx][center_idx] = self._get_room()

        self._generate_room(center_idx - 1, center_idx, 1.0)
        self._generate_room(center_idx + 1, center_idx, 1.0)
        self._generate_room(center_idx, center_idx - 1, 1.0)
        self._generate_room(center_idx, center_idx + 1, 1.0)

        self._build_rooms()
        self._shift_rooms()
        self._place_doors()
        self._populate_rooms()

        return self._dump()

    def _generate_room(self, x: int, y: int, chance: float) -> None:
        if random.uniform(0, 1) > chance:
            return

        self.grid[x][y] = self._get_room()

        decay = config.constants.GENERATOR_PROBABILITY_DECAY
        if x > 0 and not self.grid[x - 1][y]:
            self._generate_room(x - 1, y, chance * decay)
        if x < len(self.grid) - 1 and not self.grid[x + 1][y]:
            self._generate_room(x + 1, y, chance * decay)
        if y > 0 and not self.grid[x][y - 1]:
            self._generate_room(x, y - 1, chance * decay)
        if y < len(self.grid) - 1 and not self.grid[x][y + 1]:
            self._generate_room(x, y + 1, chance * decay)

    def _build_rooms(self) -> None:
        for x, room_row in enumerate(self.grid):
            for y, room in enumerate(room_row):
                if not room:
                    continue

                room.connections = self._get_neighbors(x, y)
                room.build()

    def _get_neighbors(self, x: int, y: int) -> typing.Set[RoomConnection]:
        neighbors: typing.Set[RoomConnection] = set()

        if x > 0 and self.grid[x - 1][y] is not None:
            neighbors.add(RoomConnection.LEFT)
        if x < len(self.grid) - 1 and self.grid[x + 1][y] is not None:
            neighbors.add(RoomConnection.RIGHT)
        if y > 0 and self.grid[x][y - 1] is not None:
            neighbors.add(RoomConnection.BOTTOM)
        if y < len(self.grid) - 1 and self.grid[x][y + 1] is not None:
            neighbors.add(RoomConnection.TOP)

        return neighbors

    def _shift_rooms(self) -> None:
        center_idx = math.floor(len(self.grid) / 2)
        central_room = self.grid[center_idx][center_idx]

        if not central_room:
            return

        room_dim = central_room.dim_px
        central_room_center = central_room.center
        central_room.shift(-central_room_center[0], -central_room_center[1])  # Shift central room to (0, 0)

        for x, room_row in enumerate(self.grid):
            for y, room in enumerate(room_row):
                if not room:
                    continue

                room_center = room.center
                room.shift(x * room_dim - room_center[0], y * room_dim - room_center[1])

    def _place_doors(self) -> None:
        from noname_dungeon_crawler.assets import asset_repository

        possible_rooms = [
            (x, y)
            for x, room_row in enumerate(self.grid)
            for y, room in enumerate(room_row)
            if room and RoomConnection.TOP not in room.connections
        ]

        entry_room: typing.Optional[Room] = None
        exit_room: typing.Optional[Room] = None

        max_distance = 0.0
        for entry_x, entry_y in possible_rooms:
            for exit_x, exit_y in possible_rooms:
                distance = math.sqrt((exit_x - entry_x) ** 2 + (exit_y - entry_y) ** 2)
                if distance > max_distance:
                    max_distance = distance
                    entry_room = self.grid[entry_x][entry_y]
                    exit_room = self.grid[exit_x][exit_y]

        if not entry_room or not exit_room:
            raise RuntimeError("Unable to determine entry/exit locations!")

        self._doors = arcade.SpriteList(atlas=asset_repository.texture_atlas, use_spatial_hash=True)

        self._doors.append(entry_room.make_entry())
        self._doors.append(exit_room.make_exit())

        self.starting_coords = (entry_room.center[0], entry_room.center[1] + entry_room.dim_px / 3)

    def _populate_rooms(self) -> None:
        from noname_dungeon_crawler.assets import asset_repository

        mobs = [
            entity_name for entity_name, entity in asset_repository._entities.items() if isinstance(entity, HostileMob)
        ]

        for room_row in self.grid:
            for room in room_row:
                if not room:
                    continue

                room.populate(mobs, config.constants.GENERATOR_MAX_MOBS, config.constants.GENERATOR_MAX_CHESTS)

    def _dump(self) -> _LevelDump:
        """
        Превращение матрицы и всего содержимого уровней в список спрайтов
        """
        from noname_dungeon_crawler.assets import asset_repository

        floor = arcade.SpriteList(atlas=asset_repository.texture_atlas)
        walls = arcade.SpriteList(atlas=asset_repository.texture_atlas, use_spatial_hash=True)
        mobs = arcade.SpriteList(atlas=asset_repository.texture_atlas, use_spatial_hash=True)
        chests = arcade.SpriteList(atlas=asset_repository.texture_atlas, use_spatial_hash=True)

        arcade.SpriteList()

        for room_row in self.grid:
            for room in room_row:
                if not room:
                    continue

                floor.extend(room.floor_sprites)
                walls.extend(room.wall_sprites)
                mobs.extend(room.mobs)
                chests.extend(room.chests)

        return _LevelDump(
            floor=floor, walls=walls, mobs=mobs, chests=chests, doors=self._doors, starting_coords=self.starting_coords
        )

    def _get_room(self) -> Room:
        return Room(
            size=config.constants.GENERATOR_ROOM_SIZE,
            passage_size=config.constants.GENERATOR_PASSAGE_SIZE,
            level=self.level,
        )
