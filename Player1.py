from Enhance import PlayEnhance
from CommonHeader import *
"""
    TILE_BRICK:    砖块
    TILE_STEEL:    铁
    TILE_WATER:    水
    ILE_GRASS:     草
    TILE_FROZE:    冰
    TANK_PLAYER1:  玩家1
    TANK_PLAYER2:  玩家2
    TANK_PLAYER3:  敌人
    TANK_BULLET :  子弹
    
    DIR_UP
    DIR_RIGHT
    DIR_DOWN
    DIR_LEFT
"""
TANK_CURRENT = 51


def main(tank, position):
    """
    玩家1 在此游戏
    """

    # demo
    # get my direciton
    direction = tank.direction
    # get my position
    x, y = position

    # search enemy towards
    enemies = PlayEnhance.find_enemy_towards(tank, direction)
    if len(enemies) != 0:
        tank.fire()

    for enemy in PlayEnhance.get_all_enemies():
        print(PlayEnhance.get_position(enemy))

    # search buttlets from north
    bullets = PlayEnhance.find_element(tank, DIR_UP, TANK_BULLET)
    for bullet in bullets:
        if bullet[2].direction == DIR_DOWN:
            tank.go_left()
