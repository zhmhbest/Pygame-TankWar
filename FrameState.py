import pygame
import os
from UpdateMatrix import mapping, clear_map, update_map_wall, update_map_player, update_map_enemy, print_map

"""
    操作说明
    玩家
        移动
            tank.move(DIR_UP)
            tank.move(DIR_DOWN)
            tank.move(DIR_LEFT)
            tank.move(DIR_RIGHT)
        开火
            tank.fire()
        状态: 得分 血量
            print(tank.score)
            print(tank.lives)
        位置
            my_tank_position(tank)
        朝向
            tank.direction
"""

# 道具类型
(BONUS_GRENADE, BONUS_HELMET, BONUS_SHOVEL, BONUS_STAR, BONUS_TANK, BONUS_TIMER) = range(6)

# 方向
(DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)

# 玩家
TANK_PLAYER1 = 51
TANK_PLAYER2 = 52
TANK_PLAYER3 = 53


def my_tank_position(tank):
    return mapping(tank.rect.top, tank.rect.left)


class OnPlaying:
    @staticmethod
    def game_running(game, players, enemies, bullets, bonuses):
        clear_map(game.level.map_matrix)
        update_map_wall(game.level.map_matrix, game.level.mapr)
        update_map_player(game.level.map_matrix, players)
        update_map_enemy(game.level.map_matrix, enemies)

        # print_map(game.level.map_matrix)

        OnPlaying.player_here1(players[0], game.level.map_matrix)
        if 2 == len(players):
            OnPlaying.player_here1(players[1], game.level.map_matrix)

    @staticmethod
    def player_here1(tank, map_matrix):
        """
        玩家1 在此游戏
        """
        print("玩家1", my_tank_position(tank))

    @staticmethod
    def player_here2(tank, map_matrix):
        """
        玩家2 在此游戏
        """
        print("玩家2", my_tank_position(tank))
