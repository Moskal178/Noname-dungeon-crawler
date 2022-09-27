import logging

import arcade

from .game import NonameDungeonCrawler
from .settings import config


logging.basicConfig(**config.constants.LOGGING_CONFIG)  # type: ignore

game = NonameDungeonCrawler()
game.setup()

arcade.run()
