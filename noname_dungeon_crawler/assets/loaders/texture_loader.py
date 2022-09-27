import attr
import logging
import pathlib
import typing

import arcade
from PIL import Image

from noname_dungeon_crawler.settings import config


log = logging.getLogger(__name__)


@attr.s(kw_only=True, auto_attribs=True)
class _TextureContainer:
    atlas: arcade.TextureAtlas
    static: typing.Dict[str, arcade.Texture]
    animated: typing.Dict[str, typing.List[arcade.Texture]]


class TextureLoader:
    texture_path: pathlib.Path
    texture_meta_path: pathlib.Path

    def __init__(self) -> None:
        self.image_path = config.constants.IMAGE_DIR
        self.texture_path = config.constants.TEXTURE_DIR / 'textures.png'
        self.texture_meta_path = config.constants.TEXTURE_DIR / 'textures_meta.txt'

        logging.getLogger('arcade.texture_atlas').setLevel(logging.WARNING)  # Getting rid of spammy messages

    def load_textures(self) -> _TextureContainer:
        static_textures: typing.Dict[str, arcade.Texture] = {}
        animated_textures: typing.Dict[str, typing.List[arcade.Texture]] = {}
        all_textures: typing.List[arcade.Texture] = []

        texture_file = Image.open(self.texture_path)
        meta_file = open(self.texture_meta_path, 'r')

        for texture_meta in meta_file.readlines():
            if not texture_meta or texture_meta == '\n':  # Skip empty lines
                continue

            meta_chunks = texture_meta.split()
            match len(meta_chunks):
                case 5:
                    name, x, y, w, h = meta_chunks
                    texture = self._load_texture(name, (int(x), int(y), int(w), int(h)), texture_file)
                    static_textures[name] = texture
                    all_textures.append(texture)

                case 6:
                    name, x, y, w, h, frames = meta_chunks
                    bboxes = self._make_bboxes((int(x), int(y), int(w), int(h)), int(frames))
                    textures = [self._load_texture(f'{name}_{i}', bbox, texture_file) for i, bbox in enumerate(bboxes)]
                    animated_textures[name] = textures

                    # Also load flipped texture variants for moving objects
                    flipped_textures = [
                        self._load_texture(f'{name}_{i}_flipped', bbox, texture_file, flip=True)
                        for i, bbox in enumerate(bboxes)
                    ]
                    animated_textures[f'{name}_flipped'] = flipped_textures

                    all_textures.extend(textures)

                case _:
                    log.error(f"Encountered malformed texture meta: {texture_meta}!")
                    continue

        for image_path in self.image_path.iterdir():
            if not image_path.is_file():
                continue

            image = Image.open(image_path)

            texture = arcade.Texture(image_path.stem, image)
            static_textures[image_path.stem] = texture
            all_textures.append(texture)

        atlas = arcade.TextureAtlas.create_from_texture_sequence(all_textures)

        texture_file.close()
        meta_file.close()

        return _TextureContainer(
            atlas=atlas,
            static=static_textures,
            animated=animated_textures,
        )

    def _load_texture(
        self, name: str, bbox: typing.Tuple[int, int, int, int], atlas_img: Image, flip: bool = False
    ) -> arcade.Texture:
        x, y, w, h = bbox
        texture_crop: Image = atlas_img.crop((x, y, x + w, y + h))

        if flip:
            texture_crop = texture_crop.transpose(Image.FLIP_LEFT_RIGHT)

        return arcade.Texture(name=name, image=texture_crop)

    def _make_bboxes(
        self, full_bbox: typing.Tuple[int, int, int, int], frames: int
    ) -> typing.List[typing.Tuple[int, int, int, int]]:
        x, y, w, h = full_bbox
        return [(x + w * frame, y, w, h) for frame in range(frames)]
