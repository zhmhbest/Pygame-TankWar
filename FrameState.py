import pygame
import os

"""
    操作说明
    敌军
        枚举所有敌军位置
            for enemy in enemies:
                print("敌军位置", enemy.rect.topleft)
    子弹
        枚举所有子弹位置
            for bullet in bullets:
                print("子弹位置", bullet.rect.topleft)
    道具
        枚举所有道具
            for bonuse in bonuses:
                print("道具位置, 道具类型", bonuse.rect.topleft, bonuse.bonus)
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
            tank.direction
            tank.rect.topleft
        地图信息
            game.level.mapr
"""

# 道具类型
(BONUS_GRENADE, BONUS_HELMET, BONUS_SHOVEL, BONUS_STAR, BONUS_TANK, BONUS_TIMER) = range(6)

# 方向
(DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)

# 地形常量
(TILE_EMPTY, TILE_BRICK, TILE_STEEL, TILE_WATER, TILE_GRASS, TILE_FROZE) = range(6)

# 地形像素尺寸
TILE_SIZE = 16


class OnPlaying:
    @staticmethod
    def game_running(game, players, enemies, bullets, bonuses):
        OnPlaying.player_here1(players[0], enemies, bullets, bonuses)
        if 2 == len(players):
            OnPlaying.player_here1(players[1], enemies, bullets, bonuses)
        print(game.level.mapr)


    @staticmethod
    def player_here1(tank, enemies, bullets, bonuses):
        """
        玩家1 在此游戏
        """
        print("玩家1", tank.rect.topleft)

    @staticmethod
    def player_here2(tank, enemies, bullets, bonuses):
        """
        玩家2 在此游戏
        """
        print("玩家2", tank.rect.topleft)