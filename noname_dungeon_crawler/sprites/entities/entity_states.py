import enum


class EntityDirection(enum.Enum):
    LEFT = 0
    RIGHT = 1


class EntityState(enum.Enum):
    # General
    IDLE = 'idle'
    MOVING = 'moving'

    # Living
    ATTACKING = 'attacking'
    ATTACKED = 'attacked'
    DYING = 'dying'

    # Chests
    OPENING = 'opening'
    OPENED = 'opened'

    # Trinkets
    DROPPING = 'dropping'
    PICKED_UP = 'picked_up'
