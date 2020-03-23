# -*- coding: utf-8 -*-
"""
python+pygame实现经典的《坦克大战》游戏
"""
import os
import random
import pygame

# 计时器
from Interval import gtimer

# 每帧状态
from FrameState import OnPlaying


class Castle(object):
    """ 玩家基地 """
    (STATE_STANDING, STATE_DESTROYED, STATE_EXPLODING) = range(3)

    def __init__(self):
        global sprites

        # 未被消灭的玩家基地图像
        self.img_undamaged = sprites.subsurface(0, 15 * 2, 16 * 2, 16 * 2)
        # 被消灭后的玩家基地图像
        self.img_destroyed = sprites.subsurface(16 * 2, 15 * 2, 16 * 2, 16 * 2)

        # 玩家基地位置和大小
        self.rect = pygame.Rect(12 * 16, 24 * 16, 32, 32)

        # 初始显示为未被消灭的玩家基地图像
        self.rebuild()

    def draw(self):
        """ 画玩家基地 """
        global screen

        screen.blit(self.image, self.rect.topleft)

        if self.state == self.STATE_EXPLODING:
            # 爆炸完了
            if not self.explosion.active:
                self.state = self.STATE_DESTROYED
                del self.explosion
            # 现在开始爆炸
            else:
                self.explosion.draw()

    def rebuild(self):
        """ 玩家基地 """
        self.state = self.STATE_STANDING
        self.image = self.img_undamaged
        self.active = True

    def destroy(self):
        """ 被炮弹击毁后的玩家基地 """
        # 标记为爆炸
        self.state = self.STATE_EXPLODING
        self.explosion = Explosion(self.rect.topleft)
        # 基地被击毁后的图像
        self.image = self.img_destroyed
        self.active = False


class Bonus(object):
    """
    游戏中会出现多种宝物
    宝物类型：
        手雷：敌人全灭
        头盔：暂时无敌
        铁锹：基地城墙变为钢板
        星星：火力增强
        坦克：加一条生命
        时钟：所有敌人暂停一段时间
    """
    # 宝物类型
    (BONUS_GRENADE, BONUS_HELMET, BONUS_SHOVEL, BONUS_STAR, BONUS_TANK, BONUS_TIMER) = range(6)

    def __init__(self, level):
        global sprites

        self.level = level

        self.active = True

        # 宝物是否可见
        self.visible = True

        # 随机生成宝物出现位置
        self.rect = pygame.Rect(random.randint(0, 416 - 32), random.randint(0, 416 - 32), 32, 32)

        # 随机生成出现的宝物类型
        self.bonus = random.choice([
            self.BONUS_GRENADE,
            self.BONUS_HELMET,
            self.BONUS_SHOVEL,
            self.BONUS_STAR,
            self.BONUS_TANK,
            self.BONUS_TIMER
        ])
        # 宝物图像
        self.image = sprites.subsurface(16 * 2 * self.bonus, 32 * 2, 16 * 2, 15 * 2)

    def draw(self):
        """ 画宝物到屏幕上 """
        global screen
        if self.visible:
            screen.blit(self.image, self.rect.topleft)

    def toggleVisibility(self):
        """ 切换宝物是否可见 """
        self.visible = not self.visible


class Bullet(object):
    """ 坦克炮弹 """
    # 炮弹方向
    (DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)
    # 炮弹状态
    (STATE_REMOVED, STATE_ACTIVE, STATE_EXPLODING) = range(3)
    # 炮弹属性，玩家 or 敌人
    (OWNER_PLAYER, OWNER_ENEMY) = range(2)

    def __init__(self, level, position, direction, damage=100, speed=5):
        global sprites

        self.level = level
        # 炮弹方向
        self.direction = direction
        # 炮弹伤害
        self.damage = damage

        self.owner = None
        self.owner_class = None

        # 炮弹类型：1为普通炮弹；2为加强的炮弹，可以消灭钢板
        self.power = 1

        # 炮弹图像
        self.image = sprites.subsurface(75 * 2, 74 * 2, 3 * 2, 4 * 2)

        # 重新计算炮弹方向和坐标
        if direction == self.DIR_UP:
            self.rect = pygame.Rect(position[0] + 11, position[1] - 8, 6, 8)
        elif direction == self.DIR_RIGHT:
            self.image = pygame.transform.rotate(self.image, 270)
            self.rect = pygame.Rect(position[0] + 26, position[1] + 11, 8, 6)
        elif direction == self.DIR_DOWN:
            self.image = pygame.transform.rotate(self.image, 180)
            self.rect = pygame.Rect(position[0] + 11, position[1] + 26, 6, 8)
        elif direction == self.DIR_LEFT:
            self.image = pygame.transform.rotate(self.image, 90)
            self.rect = pygame.Rect(position[0] - 8, position[1] + 11, 8, 6)

        # 炮弹爆炸效果图
        self.explosion_images = [
            sprites.subsurface(0, 80 * 2, 32 * 2, 32 * 2),
            sprites.subsurface(32 * 2, 80 * 2, 32 * 2, 32 * 2),
        ]
        # 炮弹移动速度
        self.speed = speed

        self.state = self.STATE_ACTIVE

    def draw(self):
        """ 画炮弹 """
        global screen
        if self.state == self.STATE_ACTIVE:
            screen.blit(self.image, self.rect.topleft)
        elif self.state == self.STATE_EXPLODING:
            self.explosion.draw()

    def update(self):
        global castle, players, enemies, bullets

        if self.state == self.STATE_EXPLODING:
            if not self.explosion.active:
                self.destroy()
                del self.explosion

        if self.state != self.STATE_ACTIVE:
            return

        # 计算炮弹坐标，炮弹碰撞墙壁会爆炸
        if self.direction == self.DIR_UP:
            self.rect.topleft = [self.rect.left, self.rect.top - self.speed]
            if self.rect.top < 0:
                if play_sounds and self.owner == self.OWNER_PLAYER:
                    sounds["steel"].play()
                self.explode()
                return
        elif self.direction == self.DIR_RIGHT:
            self.rect.topleft = [self.rect.left + self.speed, self.rect.top]
            if self.rect.left > (416 - self.rect.width):
                if play_sounds and self.owner == self.OWNER_PLAYER:
                    sounds["steel"].play()
                self.explode()
                return
        elif self.direction == self.DIR_DOWN:
            self.rect.topleft = [self.rect.left, self.rect.top + self.speed]
            if self.rect.top > (416 - self.rect.height):
                if play_sounds and self.owner == self.OWNER_PLAYER:
                    sounds["steel"].play()
                self.explode()
                return
        elif self.direction == self.DIR_LEFT:
            self.rect.topleft = [self.rect.left - self.speed, self.rect.top]
            if self.rect.left < 0:
                if play_sounds and self.owner == self.OWNER_PLAYER:
                    sounds["steel"].play()
                self.explode()
                return

        has_collided = False

        # 炮弹击中地形
        rects = self.level.obstacle_rects
        collisions = self.rect.collidelistall(rects)
        if collisions != []:
            for i in collisions:
                if self.level.hitTile(rects[i].topleft, self.power, self.owner == self.OWNER_PLAYER):
                    has_collided = True
        if has_collided:
            self.explode()
            return

        # 炮弹相互碰撞，则爆炸并移走该炮弹
        for bullet in bullets:
            if self.state == self.STATE_ACTIVE and bullet.owner != self.owner and bullet != self and self.rect.colliderect(
                    bullet.rect):
                self.destroy()
                self.explode()
                return

        # 炮弹击中玩家坦克
        for player in players:
            if player.state == player.STATE_ALIVE and self.rect.colliderect(player.rect):
                if player.bulletImpact(self.owner == self.OWNER_PLAYER, self.damage, self.owner_class):
                    self.destroy()
                    return

        # 炮弹击中对方坦克
        for enemy in enemies:
            if enemy.state == enemy.STATE_ALIVE and self.rect.colliderect(enemy.rect):
                if enemy.bulletImpact(self.owner == self.OWNER_ENEMY, self.damage, self.owner_class):
                    self.destroy()
                    return

        # 炮弹击中玩家基地
        if castle.active and self.rect.colliderect(castle.rect):
            castle.destroy()
            self.destroy()
            return

    def explode(self):
        """ 炮弹爆炸 """
        global screen
        if self.state != self.STATE_REMOVED:
            self.state = self.STATE_EXPLODING
            self.explosion = Explosion([self.rect.left - 13, self.rect.top - 13], None, self.explosion_images)

    def destroy(self):
        """ 标记炮弹为移除状态 """
        self.state = self.STATE_REMOVED


class Label(object):
    def __init__(self, position, text="", duration=None):
        self.position = position

        self.active = True

        self.text = text

        self.font = pygame.font.SysFont("Arial", 13)

        if duration != None:
            gtimer.add(duration, lambda: self.destroy(), 1)

    def draw(self):
        global screen
        screen.blit(self.font.render(self.text, False, (200, 200, 200)), \
                    [self.position[0] + 4, self.position[1] + 8])

    def destroy(self):
        self.active = False


class Explosion(object):
    """ 爆炸效果 """

    def __init__(self, position, interval=None, images=None):
        global sprites

        self.position = [position[0] - 16, position[1] - 16]

        # False表示已爆炸完
        self.active = True

        if interval == None:
            interval = 100

        if images == None:
            images = [
                # 三种爆炸效果
                sprites.subsurface(0, 80 * 2, 32 * 2, 32 * 2),
                sprites.subsurface(32 * 2, 80 * 2, 32 * 2, 32 * 2),
                sprites.subsurface(64 * 2, 80 * 2, 32 * 2, 32 * 2),
            ]

        images.reverse()
        self.images = [] + images
        self.image = self.images.pop()

        gtimer.add(interval, lambda: self.update(), len(self.images) + 1)

    def draw(self):
        """ 画爆炸效果 """
        global screen
        screen.blit(self.image, self.position)

    def update(self):
        if len(self.images) > 0:
            self.image = self.images.pop()
        else:
            self.active = False


class Level(object):
    """ 地形图 """
    # 地形常量
    (TILE_EMPTY, TILE_BRICK, TILE_STEEL, TILE_WATER, TILE_GRASS, TILE_FROZE) = range(6)

    # 地形像素尺寸
    TILE_SIZE = 16

    def __init__(self, level_nr=None):
        global sprites

        # 限定地形图上同时最多出现四个敌人
        self.max_active_enemies = 4

        tile_images = [
            pygame.Surface((8 * 2, 8 * 2)),
            sprites.subsurface(48 * 2, 64 * 2, 8 * 2, 8 * 2),
            sprites.subsurface(48 * 2, 72 * 2, 8 * 2, 8 * 2),
            sprites.subsurface(56 * 2, 72 * 2, 8 * 2, 8 * 2),
            sprites.subsurface(64 * 2, 64 * 2, 8 * 2, 8 * 2),
            sprites.subsurface(64 * 2, 64 * 2, 8 * 2, 8 * 2),
            sprites.subsurface(72 * 2, 64 * 2, 8 * 2, 8 * 2),
            sprites.subsurface(64 * 2, 72 * 2, 8 * 2, 8 * 2),
        ]
        self.tile_empty = tile_images[0]
        # 砖墙
        self.tile_brick = tile_images[1]
        # 钢板
        self.tile_steel = tile_images[2]
        # 森林
        self.tile_grass = tile_images[3]
        # 海水
        self.tile_water = tile_images[4]
        self.tile_water1 = tile_images[4]
        self.tile_water2 = tile_images[5]
        # 地板
        self.tile_froze = tile_images[6]

        # 一共35关，如果大于35关则从第1关继续开始，如37表示第2关
        if level_nr == None:
            level_nr = 1
        else:
            level_nr = level_nr % 35

        if level_nr == 0:
            level_nr = 35

        # 加载对应等级的地形图
        self.loadLevel(level_nr)
        # 包含所有可以被子弹消灭的地形的坐标和尺寸
        self.obstacle_rects = []
        self.updateObstacleRects()

        gtimer.add(400, lambda: self.toggleWaves())

    def hitTile(self, pos, power=1, sound=False):
        """ 炮弹击中地形的声音及地形生命计算 """
        global play_sounds, sounds

        for tile in self.mapr:
            if tile[1].topleft == pos:
                # 炮弹击中砖墙
                if tile[0] == self.TILE_BRICK:
                    if play_sounds and sound:
                        sounds["brick"].play()
                    self.mapr.remove(tile)
                    self.updateObstacleRects()
                    return True
                # 击中钢板
                elif tile[0] == self.TILE_STEEL:
                    if play_sounds and sound:
                        sounds["steel"].play()
                    if power == 2:
                        self.mapr.remove(tile)
                        self.updateObstacleRects()
                    return True
                else:
                    return False

    def toggleWaves(self):
        """ 切换海水图片 """
        if self.tile_water == self.tile_water1:
            self.tile_water = self.tile_water2
        else:
            self.tile_water = self.tile_water1

    def loadLevel(self, level_nr=1):
        """ 加载地形图文件 """
        filename = "levels/" + str(level_nr)
        if (not os.path.isfile(filename)):
            return False
        level = []
        f = open(filename, "r")
        data = f.read().split("\n")
        self.mapr = []
        x, y = 0, 0
        for row in data:
            for ch in row:
                if ch == "#":
                    self.mapr.append((self.TILE_BRICK, pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE)))
                elif ch == "@":
                    self.mapr.append((self.TILE_STEEL, pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE)))
                elif ch == "~":
                    self.mapr.append((self.TILE_WATER, pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE)))
                elif ch == "%":
                    self.mapr.append((self.TILE_GRASS, pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE)))
                elif ch == "-":
                    self.mapr.append((self.TILE_FROZE, pygame.Rect(x, y, self.TILE_SIZE, self.TILE_SIZE)))
                x += self.TILE_SIZE
            x = 0
            y += self.TILE_SIZE
        return True

    def draw(self, tiles=None):
        """ 画指定关卡的地形图到游戏窗口上 """
        global screen

        if tiles == None:
            tiles = [TILE_BRICK, TILE_STEEL, TILE_WATER, TILE_GRASS, TILE_FROZE]

        for tile in self.mapr:
            if tile[0] in tiles:
                if tile[0] == self.TILE_BRICK:
                    screen.blit(self.tile_brick, tile[1].topleft)
                elif tile[0] == self.TILE_STEEL:
                    screen.blit(self.tile_steel, tile[1].topleft)
                elif tile[0] == self.TILE_WATER:
                    screen.blit(self.tile_water, tile[1].topleft)
                elif tile[0] == self.TILE_FROZE:
                    screen.blit(self.tile_froze, tile[1].topleft)
                elif tile[0] == self.TILE_GRASS:
                    screen.blit(self.tile_grass, tile[1].topleft)

    def updateObstacleRects(self):
        """ 所有可以被子弹消灭的地形的坐标和尺寸 """
        global castle
        self.obstacle_rects = [castle.rect]  # 玩家基地是可以被子弹消灭的

        for tile in self.mapr:
            if tile[0] in (self.TILE_BRICK, self.TILE_STEEL, self.TILE_WATER):
                self.obstacle_rects.append(tile[1])

    def buildFortress(self, tile):
        """ 围绕玩家基地的砖墙 """
        positions = [
            (11 * self.TILE_SIZE, 23 * self.TILE_SIZE),
            (11 * self.TILE_SIZE, 24 * self.TILE_SIZE),
            (11 * self.TILE_SIZE, 25 * self.TILE_SIZE),
            (14 * self.TILE_SIZE, 23 * self.TILE_SIZE),
            (14 * self.TILE_SIZE, 24 * self.TILE_SIZE),
            (14 * self.TILE_SIZE, 25 * self.TILE_SIZE),
            (12 * self.TILE_SIZE, 23 * self.TILE_SIZE),
            (13 * self.TILE_SIZE, 23 * self.TILE_SIZE),
        ]

        obsolete = []

        for i, rect in enumerate(self.mapr):
            if rect[1].topleft in positions:
                obsolete.append(rect)
        for rect in obsolete:
            self.mapr.remove(rect)

        for pos in positions:
            self.mapr.append((tile, pygame.Rect(pos, [self.TILE_SIZE, self.TILE_SIZE])))

        self.updateObstacleRects()


class Tank(object):
    """ 坦克基类 """
    # 坦克方向
    (DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)
    # 坦克状态
    (STATE_SPAWNING, STATE_DEAD, STATE_ALIVE, STATE_EXPLODING) = range(4)
    # 玩家坦克 or 敌人坦克
    (SIDE_PLAYER, SIDE_ENEMY) = range(2)

    def __init__(self, level, side, position=None, direction=None, filename=None):
        global sprites

        # 坦克生命值，生命值小于1表示被消灭
        self.health = 100

        # 坦克是否瘫痪(为True则不能移动但能转向和开炮)
        self.paralised = False

        # 为True则坦克不能移动、转向和开炮
        self.paused = False

        # 坦克是否是无敌状态
        self.shielded = False

        # 移动速度，单位像素
        self.speed = 2

        # 坦克最多保持的active炮弹数
        self.max_active_bullets = 1

        # 坦克阵营
        self.side = side

        # 闪烁状态，0关闭，1开启
        self.flash = 0

        # 0表示普通坦克，1炮弹更快，2双发炮弹，3炮弹可以消灭钢板
        self.superpowers = 0

        # 为True则表示坦克被毁后会留下一个宝物
        self.bonus = None

        # 指定按键控制坦克的开火和向上、向右、向下、向左移动
        self.controls = [pygame.K_SPACE, pygame.K_UP, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT]

        # 是否按下四个方向的方向键
        self.pressed = [False] * 4

        # 坦克无敌时的状态效果
        self.shield_images = [
            sprites.subsurface(0, 48 * 2, 16 * 2, 16 * 2),
            sprites.subsurface(16 * 2, 48 * 2, 16 * 2, 16 * 2),
        ]
        self.shield_image = self.shield_images[0]
        self.shield_index = 0

        # 出现新坦克时的显示效果
        self.spawn_images = [
            sprites.subsurface(32 * 2, 48 * 2, 16 * 2, 16 * 2),
            sprites.subsurface(48 * 2, 48 * 2, 16 * 2, 16 * 2),
        ]
        self.spawn_image = self.spawn_images[0]
        self.spawn_index = 0

        self.level = level

        # 坦克出现位置
        if position != None:
            self.rect = pygame.Rect(position, (26, 26))
        else:
            self.rect = pygame.Rect(0, 0, 26, 26)

        # 坦克出现时的方向
        if direction == None:
            self.direction = random.choice([self.DIR_RIGHT, self.DIR_DOWN, self.DIR_LEFT])
        else:
            self.direction = direction

        self.state = self.STATE_SPAWNING

        # 播放新坦克出现时的效果
        self.timer_uuid_spawn = gtimer.add(100, lambda: self.toggleSpawnImage())
        # 产生新坦克的效果出现1秒后终止，并出现坦克
        self.timer_uuid_spawn_end = gtimer.add(1000, lambda: self.endSpawning())

    def endSpawning(self):
        """ 停止播放新坦克出现效果，坦克出现，可以操作 """
        self.state = self.STATE_ALIVE
        gtimer.destroy(self.timer_uuid_spawn_end)

    def toggleSpawnImage(self):
        """ 产生新坦克时的效果 """
        if self.state != self.STATE_SPAWNING:
            gtimer.destroy(self.timer_uuid_spawn)
            return
        self.spawn_index += 1
        if self.spawn_index >= len(self.spawn_images):
            self.spawn_index = 0
        # 每回调该方法一次，切换一次图像
        self.spawn_image = self.spawn_images[self.spawn_index]

    def toggleShieldImage(self):
        """ 用于坦克的无敌状态显示 """
        if self.state != self.STATE_ALIVE:
            gtimer.destroy(self.timer_uuid_shield)
            return
        if self.shielded:
            self.shield_index += 1
            if self.shield_index >= len(self.shield_images):
                self.shield_index = 0
            # 每回调该方法一次，切换一次图像
            self.shield_image = self.shield_images[self.shield_index]

    def draw(self):
        """ 画坦克 """
        global screen
        if self.state == self.STATE_ALIVE:
            screen.blit(self.image, self.rect.topleft)
            if self.shielded:
                screen.blit(self.shield_image, [self.rect.left - 3, self.rect.top - 3])
        # 坦克爆炸
        elif self.state == self.STATE_EXPLODING:
            self.explosion.draw()
        # 产生新坦克
        elif self.state == self.STATE_SPAWNING:
            screen.blit(self.spawn_image, self.rect.topleft)

    def explode(self):
        """ 坦克爆炸 """
        if self.state != self.STATE_DEAD:
            self.state = self.STATE_EXPLODING
            self.explosion = Explosion(self.rect.topleft)

            if self.bonus:
                self.spawnBonus()  # 坦克爆炸后出现宝物

    def fire(self, forced=False):
        """
        发射子弹
        返回True表示已发射子弹，False为其他
        """
        global bullets, labels

        # 坦克被消灭，不再发射炮弹
        if self.state != self.STATE_ALIVE:
            gtimer.destroy(self.timer_uuid_fire)
            return False

        if self.paused:
            return False

        if not forced:
            # 同一辆坦克只能保持一定的active炮弹数
            # 游戏窗口内最多属于同一辆坦克的炮弹数
            active_bullets = 0
            for bullet in bullets:
                if bullet.owner_class == self and bullet.state == bullet.STATE_ACTIVE:
                    active_bullets += 1
            if active_bullets >= self.max_active_bullets:
                return False

        bullet = Bullet(self.level, self.rect.topleft, self.direction)

        if self.superpowers > 0:
            bullet.speed = 8

        if self.superpowers > 2:
            bullet.power = 2

        if self.side == self.SIDE_PLAYER:
            bullet.owner = self.SIDE_PLAYER
        else:
            bullet.owner = self.SIDE_ENEMY
            self.bullet_queued = False

        bullet.owner_class = self
        bullets.append(bullet)
        return True

    def rotate(self, direction, fix_position=True):
        """ 坦克转向 """
        self.direction = direction

        # 加载对应方向的坦克图像
        if direction == self.DIR_UP:
            self.image = self.image_up
        elif direction == self.DIR_RIGHT:
            self.image = self.image_right
        elif direction == self.DIR_DOWN:
            self.image = self.image_down
        elif direction == self.DIR_LEFT:
            self.image = self.image_left

        if fix_position:
            new_x = self.nearest(self.rect.left, 8) + 3
            new_y = self.nearest(self.rect.top, 8) + 3

            if (abs(self.rect.left - new_x) < 5):
                self.rect.left = new_x

            if (abs(self.rect.top - new_y) < 5):
                self.rect.top = new_y

    def turnAround(self):
        """ 坦克朝向相反方向 """
        if self.direction in (self.DIR_UP, self.DIR_RIGHT):
            self.rotate(self.direction + 2, False)
        else:
            self.rotate(self.direction - 2, False)

    def update(self, time_passed):
        if self.state == self.STATE_EXPLODING:
            if not self.explosion.active:
                self.state = self.STATE_DEAD
                del self.explosion

    def nearest(self, num, base):
        return int(round(num / (base * 1.0)) * base)

    def bulletImpact(self, friendly_fire=False, damage=100, tank=None):
        """ 子弹碰撞规则，敌方坦克被敌方炮弹击中不会爆炸 """
        global play_sounds, sounds

        # 坦克处于无敌状态中
        if self.shielded:
            return True

        # 坦克被对方坦克炮弹击中
        if not friendly_fire:
            self.health -= damage
            if self.health < 1:
                # 敌方坦克被击中，计分
                if self.side == self.SIDE_ENEMY:
                    tank.trophies["enemy" + str(self.type)] += 1
                    points = (self.type + 1) * 100
                    tank.score += points
                    if play_sounds:
                        sounds["explosion"].play()

                    labels.append(Label(self.rect.topleft, str(points), 500))

                # 坦克爆炸
                self.explode()
            return True

        # 敌方坦克被敌方炮弹击中
        if self.side == self.SIDE_ENEMY:
            return False

        # 玩家坦克被玩家炮弹击中，会进入瘫痪状态
        elif self.side == self.SIDE_PLAYER:
            if not self.paralised:
                self.setParalised(True)
                self.timer_uuid_paralise = gtimer.add(10000, lambda: self.setParalised(False), 1)
            return True

    def setParalised(self, paralised=True):
        """ 坦克瘫痪状态 """
        if self.state != self.STATE_ALIVE:
            gtimer.destroy(self.timer_uuid_paralise)
            return
        self.paralised = paralised


class Enemy(Tank):
    """ 敌方坦克 """
    # 四种类似的坦克
    (TYPE_BASIC, TYPE_FAST, TYPE_POWER, TYPE_ARMOR) = range(4)

    def __init__(self, level, type, position=None, direction=None, filename=None):
        Tank.__init__(self, level, type, position=None, direction=None, filename=None)

        global enemies, sprites

        # 为True则不开火
        self.bullet_queued = False

        # 随机出现坦克类型
        if len(level.enemies_left) > 0:
            self.type = level.enemies_left.pop()
        else:
            self.state = self.STATE_DEAD
            return

        if self.type == self.TYPE_BASIC:
            self.speed = 1
        elif self.type == self.TYPE_FAST:
            self.speed = 3
        elif self.type == self.TYPE_POWER:
            self.superpowers = 1
        elif self.type == self.TYPE_ARMOR:
            self.health = 400

        # 敌方坦克爆炸后有五分之一机会留下一个宝物
        # 且场上同时只能有一个宝物
        if random.randint(1, 5) == 1:
            self.bonus = True
            for enemy in enemies:
                if enemy.bonus:
                    self.bonus = False
                    break

        images = [
            sprites.subsurface(32 * 2, 0, 13 * 2, 15 * 2),
            sprites.subsurface(48 * 2, 0, 13 * 2, 15 * 2),
            sprites.subsurface(64 * 2, 0, 13 * 2, 15 * 2),
            sprites.subsurface(80 * 2, 0, 13 * 2, 15 * 2),
            sprites.subsurface(32 * 2, 16 * 2, 13 * 2, 15 * 2),
            sprites.subsurface(48 * 2, 16 * 2, 13 * 2, 15 * 2),
            sprites.subsurface(64 * 2, 16 * 2, 13 * 2, 15 * 2),
            sprites.subsurface(80 * 2, 16 * 2, 13 * 2, 15 * 2)
        ]

        self.image = images[self.type + 0]

        self.image_up = self.image;
        self.image_left = pygame.transform.rotate(self.image, 90)
        self.image_down = pygame.transform.rotate(self.image, 180)
        self.image_right = pygame.transform.rotate(self.image, 270)

        if self.bonus:
            self.image1_up = self.image_up;
            self.image1_left = self.image_left
            self.image1_down = self.image_down
            self.image1_right = self.image_right

            self.image2 = images[self.type + 4]
            self.image2_up = self.image2;
            self.image2_left = pygame.transform.rotate(self.image2, 90)
            self.image2_down = pygame.transform.rotate(self.image2, 180)
            self.image2_right = pygame.transform.rotate(self.image2, 270)

        self.rotate(self.direction, False)

        # 敌方坦克出现位置
        if position == None:
            self.rect.topleft = self.getFreeSpawningPosition()
            if not self.rect.topleft:
                self.state = self.STATE_DEAD
                return

        # 计算坦克自动移动路径
        self.path = self.generatePath(self.direction)

        # 每秒发射一颗子弹
        self.timer_uuid_fire = gtimer.add(1000, lambda: self.fire())

        # 宝物闪烁
        if self.bonus:
            self.timer_uuid_flash = gtimer.add(200, lambda: self.toggleFlash())

    def toggleFlash(self):
        """ 切换闪烁状态 """
        if self.state not in (self.STATE_ALIVE, self.STATE_SPAWNING):
            gtimer.destroy(self.timer_uuid_flash)
            return
        self.flash = not self.flash
        if self.flash:
            self.image_up = self.image2_up
            self.image_right = self.image2_right
            self.image_down = self.image2_down
            self.image_left = self.image2_left
        else:
            self.image_up = self.image1_up
            self.image_right = self.image1_right
            self.image_down = self.image1_down
            self.image_left = self.image1_left
        self.rotate(self.direction, False)

    def spawnBonus(self):
        """ 产生新的宝物 """

        global bonuses

        if len(bonuses) > 0:
            return
        bonus = Bonus(self.level)
        bonuses.append(bonus)
        gtimer.add(500, lambda: bonus.toggleVisibility())
        gtimer.add(10000, lambda: bonuses.remove(bonus), 1)

    def getFreeSpawningPosition(self):
        global players, enemies

        available_positions = [
            [(self.level.TILE_SIZE * 2 - self.rect.width) / 2, (self.level.TILE_SIZE * 2 - self.rect.height) / 2],
            [12 * self.level.TILE_SIZE + (self.level.TILE_SIZE * 2 - self.rect.width) / 2,
             (self.level.TILE_SIZE * 2 - self.rect.height) / 2],
            [24 * self.level.TILE_SIZE + (self.level.TILE_SIZE * 2 - self.rect.width) / 2,
             (self.level.TILE_SIZE * 2 - self.rect.height) / 2]
        ]

        random.shuffle(available_positions)

        # 随机挑选一个没被其他物体占用的坐标出现新坦克
        for pos in available_positions:
            enemy_rect = pygame.Rect(pos, [26, 26])

            collision = False
            for enemy in enemies:
                if enemy_rect.colliderect(enemy.rect):
                    collision = True
                    continue

            if collision:
                continue

            collision = False
            for player in players:
                if enemy_rect.colliderect(player.rect):
                    collision = True
                    continue

            if collision:
                continue

            return pos
        return False

    def move(self):
        """ 敌方坦克移动 """
        global players, enemies, bonuses

        if self.state != self.STATE_ALIVE or self.paused or self.paralised:
            return

        # 生成自动移动路径
        if self.path == []:
            self.path = self.generatePath(None, True)

        new_position = self.path.pop(0)

        # 坦克下一个出现位置超出游戏界面，则重新计算自动移动路径
        if self.direction == self.DIR_UP:
            if new_position[1] < 0:
                self.path = self.generatePath(self.direction, True)
                return
        elif self.direction == self.DIR_RIGHT:
            if new_position[0] > (416 - 26):
                self.path = self.generatePath(self.direction, True)
                return
        elif self.direction == self.DIR_DOWN:
            if new_position[1] > (416 - 26):
                self.path = self.generatePath(self.direction, True)
                return
        elif self.direction == self.DIR_LEFT:
            if new_position[0] < 0:
                self.path = self.generatePath(self.direction, True)
                return

        new_rect = pygame.Rect(new_position, [26, 26])

        # 撞上地形，重新计算坦克自动移动路径
        if new_rect.collidelist(self.level.obstacle_rects) != -1:
            self.path = self.generatePath(self.direction, True)
            return

        # 撞上其他敌方坦克，坦克转向反方向，并重新计算坦克自动移动路径
        for enemy in enemies:
            if enemy != self and new_rect.colliderect(enemy.rect):
                self.turnAround()
                self.path = self.generatePath(self.direction)
                return

        # 撞上玩家坦克，坦克转向反方向，并重新计算坦克自动移动路径
        for player in players:
            if new_rect.colliderect(player.rect):
                self.turnAround()
                self.path = self.generatePath(self.direction)
                return

        # 撞上宝物，宝物消失，敌人坦克不会获得任何增益效果
        for bonus in bonuses:
            if new_rect.colliderect(bonus.rect):
                bonuses.remove(bonus)

        # 没撞上任何东西，则将坐标设置为坦克移动的下一个坐标
        self.rect.topleft = new_rect.topleft

    def update(self, time_passed):
        Tank.update(self, time_passed)
        if self.state == self.STATE_ALIVE and not self.paused:
            self.move()

    def generatePath(self, direction=None, fix_direction=False):
        """
        敌方坦克自动移动规则：
        先沿着坦克指向方向走，不通则随机选择一个方向
        """
        all_directions = [self.DIR_UP, self.DIR_RIGHT, self.DIR_DOWN, self.DIR_LEFT]

        if direction == None:
            if self.direction in [self.DIR_UP, self.DIR_RIGHT]:
                opposite_direction = self.direction + 2
            else:
                opposite_direction = self.direction - 2
            directions = all_directions
            # 打乱方向顺序
            random.shuffle(directions)
            # 将坦克方向的相反方向放到最后，最后才选择反方向移动
            directions.remove(opposite_direction)
            directions.append(opposite_direction)
        else:
            if direction in [self.DIR_UP, self.DIR_RIGHT]:
                opposite_direction = direction + 2
            else:
                opposite_direction = direction - 2
            directions = all_directions
            random.shuffle(directions)
            directions.remove(opposite_direction)
            directions.remove(direction)
            # 优先选择坦克方向移动
            directions.insert(0, direction)
            # 最后选择坦克方向相反方向移动
            directions.append(opposite_direction)

        x = int(round(self.rect.left / 16))
        y = int(round(self.rect.top / 16))

        new_direction = None

        # 朝首选的指定方向移动8像素，如果超出游戏界面，则转向反方向
        # 如果与地形障碍物碰撞，转为其他方向继续尝试
        for direction in directions:
            if direction == self.DIR_UP and y > 1:
                new_pos_rect = self.rect.move(0, -8)
                if new_pos_rect.collidelist(self.level.obstacle_rects) == -1:
                    new_direction = direction
                    break
            elif direction == self.DIR_RIGHT and x < 24:
                new_pos_rect = self.rect.move(8, 0)
                if new_pos_rect.collidelist(self.level.obstacle_rects) == -1:
                    new_direction = direction
                    break
            elif direction == self.DIR_DOWN and y < 24:
                new_pos_rect = self.rect.move(0, 8)
                if new_pos_rect.collidelist(self.level.obstacle_rects) == -1:
                    new_direction = direction
                    break
            elif direction == self.DIR_LEFT and x > 1:
                new_pos_rect = self.rect.move(-8, 0)
                if new_pos_rect.collidelist(self.level.obstacle_rects) == -1:
                    new_direction = direction
                    break

        # 超出游戏界面，转为反方向
        if new_direction == None:
            new_direction = opposite_direction

        # 如果坦克继续沿着坦克当前方向移动，则无须修正坐标
        if fix_direction and new_direction == self.direction:
            fix_direction = False

        # 坦克转向并修正转向后的坐标
        self.rotate(new_direction, fix_direction)

        positions = []

        x = self.rect.left
        y = self.rect.top

        if new_direction in (self.DIR_RIGHT, self.DIR_LEFT):
            axis_fix = self.nearest(y, 16) - y
        else:
            axis_fix = self.nearest(x, 16) - x
        axis_fix = 0

        pixels = self.nearest(random.randint(1, 12) * 32, 32) + axis_fix + 3

        # 计算自动移动路径
        if new_direction == self.DIR_UP:
            for px in range(0, pixels, self.speed):
                positions.append([x, y - px])
        elif new_direction == self.DIR_RIGHT:
            for px in range(0, pixels, self.speed):
                positions.append([x + px, y])
        elif new_direction == self.DIR_DOWN:
            for px in range(0, pixels, self.speed):
                positions.append([x, y + px])
        elif new_direction == self.DIR_LEFT:
            for px in range(0, pixels, self.speed):
                positions.append([x - px, y])

        return positions


class Player(Tank):
    """ 玩家坦克 """

    def __init__(self, level, type, position=None, direction=None, filename=None):
        Tank.__init__(self, level, type, position=None, direction=None, filename=None)
        global sprites

        if filename == None:
            filename = (0, 0, 16 * 2, 16 * 2)
        # 出现位置和方向
        self.start_position = position
        self.start_direction = direction
        # 生命
        self.lives = 3

        # 得分
        self.score = 0

        # 收集宝物数量和消灭敌方坦克数量
        self.trophies = {
            "bonus": 0,
            "enemy0": 0,
            "enemy1": 0,
            "enemy2": 0,
            "enemy3": 0
        }

        # 玩家坦克图像
        self.image = sprites.subsurface(filename)
        self.image_up = self.image
        self.image_left = pygame.transform.rotate(self.image, 90)
        self.image_down = pygame.transform.rotate(self.image, 180)
        self.image_right = pygame.transform.rotate(self.image, 270)

        # 玩家坦克方向默认向上
        if direction == None:
            self.rotate(self.DIR_UP, False)
        else:
            self.rotate(direction, False)

    def move(self, direction):
        """ 玩家坦克移动 """
        global players, enemies, bonuses

        if self.state == self.STATE_EXPLODING:
            if not self.explosion.active:
                self.state = self.STATE_DEAD
                del self.explosion

        if self.state != self.STATE_ALIVE:
            return

        # 坦克转向
        if self.direction != direction:
            self.rotate(direction)

        if self.paralised:
            return

        # 计算坦克出现的新位置，不能超出游戏窗口范围
        if direction == self.DIR_UP:
            new_position = [self.rect.left, self.rect.top - self.speed]
            if new_position[1] < 0:
                return
        elif direction == self.DIR_RIGHT:
            new_position = [self.rect.left + self.speed, self.rect.top]
            if new_position[0] > (416 - 26):
                return
        elif direction == self.DIR_DOWN:
            new_position = [self.rect.left, self.rect.top + self.speed]
            if new_position[1] > (416 - 26):
                return
        elif direction == self.DIR_LEFT:
            new_position = [self.rect.left - self.speed, self.rect.top]
            if new_position[0] < 0:
                return

        player_rect = pygame.Rect(new_position, [26, 26])

        # 撞上地形
        if player_rect.collidelist(self.level.obstacle_rects) != -1:
            return

        # 撞上其它玩家坦克
        for player in players:
            if player != self and player.state == player.STATE_ALIVE and player_rect.colliderect(player.rect) == True:
                return

        # 撞上敌方坦克
        for enemy in enemies:
            if player_rect.colliderect(enemy.rect) == True:
                return

        # 撞上宝物
        for bonus in bonuses:
            if player_rect.colliderect(bonus.rect) == True:
                self.bonus = bonus

        # 更新玩家坦克出现的新坐标（没撞上任何阻挡物和没超出游戏窗口）
        self.rect.topleft = (new_position[0], new_position[1])

    def reset(self):
        """ 重新初始化玩家坦克状态 """
        self.rotate(self.start_direction, False)
        self.rect.topleft = self.start_position
        self.superpowers = 0
        self.max_active_bullets = 1
        self.health = 100
        self.paralised = False
        self.paused = False
        self.pressed = [False] * 4
        self.state = self.STATE_ALIVE


class Game(object):
    # 方向
    (DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)
    TILE_SIZE = 16

    def __init__(self):
        global screen, sprites, play_sounds, sounds
        # 游戏窗口位于屏幕中央
        os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'

        if play_sounds:
            # 预设mixer初始化参数，必须位于pygame.init()之前
            pygame.mixer.pre_init(44100, -16, 1, 512)

        pygame.init()
        size = width, height = 480, 416
        # 创建游戏窗口
        screen = pygame.display.set_mode(size)
        # 游戏窗口的文字标题
        pygame.display.set_caption("坦克大战")
        # 用于设置帧速
        self.clock = pygame.time.Clock()

        # 游戏中所有图片资源都在这里了
        sprites = pygame.transform.scale(pygame.image.load("images/sprites.gif"), [192, 224])

        # 设置游戏窗口的图形标题，默认为pygame官方图标
        pygame.display.set_icon(sprites.subsurface(0, 0, 13 * 2, 13 * 2))

        if play_sounds:
            pygame.mixer.init(44100, -16, 1, 512)
            # 加载声音文件
            sounds["start"] = pygame.mixer.Sound("sounds/gamestart.ogg")
            sounds["end"] = pygame.mixer.Sound("sounds/gameover.ogg")
            sounds["score"] = pygame.mixer.Sound("sounds/score.ogg")
            sounds["bg"] = pygame.mixer.Sound("sounds/background.ogg")
            sounds["fire"] = pygame.mixer.Sound("sounds/fire.ogg")
            sounds["bonus"] = pygame.mixer.Sound("sounds/bonus.ogg")
            sounds["explosion"] = pygame.mixer.Sound("sounds/explosion.ogg")
            sounds["brick"] = pygame.mixer.Sound("sounds/brick.ogg")
            sounds["steel"] = pygame.mixer.Sound("sounds/steel.ogg")

        # 表示还有多少个敌人
        self.enemy_life_image = sprites.subsurface(81 * 2, 57 * 2, 7 * 2, 7 * 2)
        # 表示自己还有多少条生命
        self.player_life_image = sprites.subsurface(89 * 2, 56 * 2, 7 * 2, 8 * 2)
        # 表示第几关
        self.flag_image = sprites.subsurface(64 * 2, 49 * 2, 16 * 2, 15 * 2)

        # 用在选择界面，选择单人模式还是双人模式
        self.player_image = pygame.transform.rotate(sprites.subsurface(0, 0, 13 * 2, 13 * 2), 270)

        self.timefreeze = False

        # 加载自定义字体，字体大小为16
        # self.font = pygame.font.Font("fonts/prstart.ttf", 16)
        self.font = pygame.font.Font("fonts/heiti.ttf", 16)

        # 游戏结束画面
        self.im_game_over = pygame.Surface((64, 40))
        self.im_game_over.set_colorkey((0, 0, 0))
        self.im_game_over.blit(self.font.render("GAME", False, (127, 64, 64)), [0, 0])
        self.im_game_over.blit(self.font.render("OVER", False, (127, 64, 64)), [0, 20])
        self.game_over_y = 416 + 40

        # 默认为单人游戏
        self.nr_of_players = 1

        # 初始化游戏环境
        del players[:]
        del bullets[:]
        del enemies[:]
        del bonuses[:]

    def triggerBonus(self, bonus, player):
        """ 触发宝物效果 """

        global enemies, labels, play_sounds, sounds

        if play_sounds:
            sounds["bonus"].play()

        # 玩家坦克吃宝物数量
        player.trophies["bonus"] += 1
        player.score += 500

        # 手雷宝物效果
        if bonus.bonus == bonus.BONUS_GRENADE:
            for enemy in enemies:
                enemy.explode()
        # 头盔宝物效果
        elif bonus.bonus == bonus.BONUS_HELMET:
            self.shieldPlayer(player, True, 10000)
        # 铁锹宝物效果
        elif bonus.bonus == bonus.BONUS_SHOVEL:
            self.level.buildFortress(self.level.TILE_STEEL)
            gtimer.add(10000, lambda: self.level.buildFortress(self.level.TILE_BRICK), 1)
        # 星星宝物效果
        elif bonus.bonus == bonus.BONUS_STAR:
            player.superpowers += 1
            if player.superpowers == 2:
                player.max_active_bullets = 2
        # 坦克宝物效果
        elif bonus.bonus == bonus.BONUS_TANK:
            player.lives += 1
        # 时钟宝物效果
        elif bonus.bonus == bonus.BONUS_TIMER:
            self.toggleEnemyFreeze(True)
            gtimer.add(10000, lambda: self.toggleEnemyFreeze(False), 1)
        bonuses.remove(bonus)

        labels.append(Label(bonus.rect.topleft, "500", 500))

    def shieldPlayer(self, player, shield=True, duration=None):
        """
        玩家坦克刚出现时有短暂的无敌状态
        该方法用于添加/移除玩家的无敌状态
        """
        player.shielded = shield
        if shield:
            player.timer_uuid_shield = gtimer.add(100, lambda: player.toggleShieldImage())
        else:
            gtimer.destroy(player.timer_uuid_shield)

        if shield and duration != None:
            gtimer.add(duration, lambda: self.shieldPlayer(player, False), 1)

    def spawnEnemy(self):
        """ 产生敌方坦克 """
        global enemies

        if len(enemies) >= self.level.max_active_enemies:
            return
        if len(self.level.enemies_left) < 1 or self.timefreeze:
            return
        enemy = Enemy(self.level, 1)

        enemies.append(enemy)

    def respawnPlayer(self, player, clear_scores=False):
        # 初始化玩家坦克属性
        player.reset()

        # 清除玩家所有得分
        if clear_scores:
            player.trophies = {
                "bonus": 0, "enemy0": 0, "enemy1": 0, "enemy2": 0, "enemy3": 0
            }

        # 玩家坦克出现时的无敌效果显示，默认4秒无敌
        self.shieldPlayer(player, True, 4000)

    def gameOver(self):
        """ 游戏结束 """
        global play_sounds, sounds

        print("Game Over")
        if play_sounds:
            for sound in sounds:
                sounds[sound].stop()
            sounds["end"].play()

        self.game_over_y = 416 + 40

        self.game_over = True
        gtimer.add(3000, lambda: self.showScores(), 1)

    def gameOverScreen(self):
        """ 显示游戏结束界面 """
        global screen

        # 结束游戏主循环
        self.running = False

        screen.fill([0, 0, 0])

        self.writeInBricks("game", [125, 140])
        self.writeInBricks("over", [125, 220])
        pygame.display.flip()

        while True:
            time_passed = self.clock.tick(50)
            for event in pygame.event.get():
                # 按关闭按钮退出游戏
                if event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.KEYDOWN:
                    # 按回车显示选择界面
                    if event.key == pygame.K_RETURN:
                        self.showMenu()
                        return

    def showMenu(self):
        """ 选择界面，接收用户的选择并进入下一关 """
        global players, screen

        self.running = False
        del gtimer.timers[:]
        # 0关就是选择界面
        self.stage = 0

        # 把选择界面画到游戏窗口中
        self.animateIntroScreen()

        main_loop = True
        while main_loop:
            # 每秒50帧
            time_passed = self.clock.tick(50)

            for event in pygame.event.get():
                # 点击关闭按钮，退出游戏
                if event.type == pygame.QUIT:
                    quit()
                # 选择单人模式还是双人模式的逻辑
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        # 按了方向键向上键，如果之前是指向双人模式，则需要重画选择画面，以便指向单人模式
                        if self.nr_of_players == 2:
                            self.nr_of_players = 1
                            self.drawIntroScreen()
                    elif event.key == pygame.K_DOWN:
                        if self.nr_of_players == 1:
                            self.nr_of_players = 2
                            self.drawIntroScreen()
                    elif event.key == pygame.K_RETURN:  # 按回车键，结束选择
                        main_loop = False

        del players[:]
        self.nextLevel()

    def reloadPlayers(self):
        """ 初始化玩家坦克 """
        global players

        if len(players) == 0:
            # 玩家一
            x = 8 * self.TILE_SIZE + (self.TILE_SIZE * 2 - 26) / 2
            y = 24 * self.TILE_SIZE + (self.TILE_SIZE * 2 - 26) / 2

            player = Player(
                self.level, 0, [x, y], self.DIR_UP, (0, 0, 13 * 2, 13 * 2)
            )
            players.append(player)

            # 玩家二
            if self.nr_of_players == 2:
                x = 16 * self.TILE_SIZE + (self.TILE_SIZE * 2 - 26) / 2
                y = 24 * self.TILE_SIZE + (self.TILE_SIZE * 2 - 26) / 2
                player = Player(
                    self.level, 0, [x, y], self.DIR_UP, (16 * 2, 0, 13 * 2, 13 * 2)
                )
                player.controls = [102, 119, 100, 115, 97]
                players.append(player)

        for player in players:
            player.level = self.level
            self.respawnPlayer(player, True)

    def showScores(self):
        """ 计分页面 """
        global screen, sprites, players, play_sounds, sounds

        # 终止游戏主循环
        self.running = False

        # 清除所有计时器
        del gtimer.timers[:]

        # 停止播放所有的游戏声音
        if play_sounds:
            for sound in sounds:
                sounds[sound].stop()

        # 加载历史游戏得分
        hiscore = self.loadHiscore()

        if players[0].score > hiscore:
            hiscore = players[0].score
            self.saveHiscore(hiscore)
        if self.nr_of_players == 2 and players[1].score > hiscore:
            hiscore = players[1].score
            self.saveHiscore(hiscore)

        img_tanks = [
            sprites.subsurface(32 * 2, 0, 13 * 2, 15 * 2),
            sprites.subsurface(48 * 2, 0, 13 * 2, 15 * 2),
            sprites.subsurface(64 * 2, 0, 13 * 2, 15 * 2),
            sprites.subsurface(80 * 2, 0, 13 * 2, 15 * 2)
        ]

        img_arrows = [
            sprites.subsurface(81 * 2, 48 * 2, 7 * 2, 7 * 2),
            sprites.subsurface(88 * 2, 48 * 2, 7 * 2, 7 * 2)
        ]

        # 把游戏窗口填充为黑色，方便后面显示
        screen.fill([0, 0, 0])

        # 颜色
        black = pygame.Color("black")
        white = pygame.Color("white")
        purple = pygame.Color(127, 64, 64)
        pink = pygame.Color(191, 160, 128)

        screen.blit(self.font.render(u"最高得分", False, purple), [105, 35])
        screen.blit(self.font.render(str(hiscore), False, pink), [295, 35])

        screen.blit(self.font.render(u"关卡" + str(self.stage).rjust(3), False, white), [170, 65])

        screen.blit(self.font.render(u"玩家一", False, purple), [25, 95])

        # 玩家1得分
        screen.blit(self.font.render(str(players[0].score).rjust(8), False, pink), [25, 125])

        if self.nr_of_players == 2:
            screen.blit(self.font.render(u"玩家二", False, purple), [320, 95])

            # 玩家2得分
            screen.blit(self.font.render(str(players[1].score).rjust(8), False, pink), [325, 125])

        # 画坦克图像
        for i in range(4):
            screen.blit(img_tanks[i], [226, 160 + (i * 45)])
            screen.blit(img_arrows[0], [206, 168 + (i * 45)])
            if self.nr_of_players == 2:
                screen.blit(img_arrows[1], [258, 168 + (i * 45)])

        screen.blit(self.font.render("TOTAL", False, white), [70, 335])

        pygame.draw.line(screen, white, [170, 330], [307, 330], 4)

        pygame.display.flip()

        self.clock.tick(2)

        interval = 5

        # 开始计分，显示玩家消灭坦克数和相关得分
        for i in range(4):

            tanks = players[0].trophies["enemy" + str(i)]

            for n in range(tanks + 1):
                if n > 0 and play_sounds:
                    sounds["score"].play()

                screen.blit(self.font.render(str(n - 1).rjust(2), False, black), [170, 168 + (i * 45)])
                screen.blit(self.font.render(str(n).rjust(2), False, white), [170, 168 + (i * 45)])
                screen.blit(self.font.render(str((n - 1) * (i + 1) * 100).rjust(4) + " PTS", False, black),
                            [25, 168 + (i * 45)])
                screen.blit(self.font.render(str(n * (i + 1) * 100).rjust(4) + " PTS", False, white),
                            [25, 168 + (i * 45)])
                pygame.display.flip()
                self.clock.tick(interval)

            if self.nr_of_players == 2:
                tanks = players[1].trophies["enemy" + str(i)]

                for n in range(tanks + 1):

                    if n > 0 and play_sounds:
                        sounds["score"].play()

                    screen.blit(self.font.render(str(n - 1).rjust(2), False, black), [277, 168 + (i * 45)])
                    screen.blit(self.font.render(str(n).rjust(2), False, white), [277, 168 + (i * 45)])

                    screen.blit(self.font.render(str((n - 1) * (i + 1) * 100).rjust(4) + " PTS", False, black),
                                [325, 168 + (i * 45)])
                    screen.blit(self.font.render(str(n * (i + 1) * 100).rjust(4) + " PTS", False, white),
                                [325, 168 + (i * 45)])

                    pygame.display.flip()
                    self.clock.tick(interval)

            self.clock.tick(interval)

        tanks = sum([i for i in players[0].trophies.values()]) - players[0].trophies["bonus"]
        screen.blit(self.font.render(str(tanks).rjust(2), False, white), [170, 335])
        if self.nr_of_players == 2:
            tanks = sum([i for i in players[1].trophies.values()]) - players[1].trophies["bonus"]
            screen.blit(self.font.render(str(tanks).rjust(2), False, white), [277, 335])

        pygame.display.flip()

        # 在积分页面停留2秒
        self.clock.tick(1)
        self.clock.tick(1)

        if self.game_over:
            self.gameOverScreen()  # 结束界面
        else:
            self.nextLevel()

    def draw(self):
        global screen, castle, players, enemies, bullets, bonuses
        # 先填充为黑色
        screen.fill([0, 0, 0])
        # 画地形图
        self.level.draw([self.level.TILE_EMPTY, self.level.TILE_BRICK, \
                         self.level.TILE_STEEL, self.level.TILE_FROZE, \
                         self.level.TILE_WATER])
        # 画玩家基地
        castle.draw()

        for enemy in enemies:
            enemy.draw()

        for label in labels:
            label.draw()

        for player in players:
            player.draw()

        for bullet in bullets:
            bullet.draw()

        for bonus in bonuses:
            bonus.draw()

        self.level.draw([self.level.TILE_GRASS])

        # 游戏结束了的话，显示"game over"，从基地位置移到屏幕中间，每帧移动4像素
        if self.game_over:
            if self.game_over_y > 188:
                self.game_over_y -= 4
            screen.blit(self.im_game_over, [176, self.game_over_y])  # 176=(416-64)/2

        # 画侧边栏，显示敌人生命，玩家生命
        self.drawSidebar()

        pygame.display.flip()

    def drawSidebar(self):
        """ 画侧边栏 """
        global screen, players, enemies

        x = 416
        y = 0
        screen.fill([100, 100, 100], pygame.Rect([416, 0], [64, 416]))

        xpos = x + 16
        ypos = y + 16

        # 画敌人生命
        for n in range(len(self.level.enemies_left) + len(enemies)):
            screen.blit(self.enemy_life_image, [xpos, ypos])
            if n % 2 == 1:
                xpos = x + 16
                ypos += 17
            else:
                xpos += 17

        # 画玩家生命
        if pygame.font.get_init():
            text_color = pygame.Color('black')
            for n in range(len(players)):
                if n == 0:
                    screen.blit(self.font.render(str(n + 1) + "P", False, text_color), [x + 16, y + 200])
                    screen.blit(self.font.render(str(players[n].lives), False, text_color), [x + 31, y + 215])
                    screen.blit(self.player_life_image, [x + 17, y + 215])
                else:
                    screen.blit(self.font.render(str(n + 1) + "P", False, text_color), [x + 16, y + 240])
                    screen.blit(self.font.render(str(players[n].lives), False, text_color), [x + 31, y + 255])
                    screen.blit(self.player_life_image, [x + 17, y + 255])

            screen.blit(self.flag_image, [x + 17, y + 280])
            screen.blit(self.font.render(str(self.stage), False, text_color), [x + 17, y + 312])

    def drawIntroScreen(self, put_on_surface=True):
        """ 画选择界面 """
        global screen
        # 先把游戏窗口填充为全黑
        screen.fill((0, 0, 0))

        self.writeInBricks("battle", [65, 80])
        self.writeInBricks("city", [129, 160])

        if pygame.font.get_init():
            # 之前获得的最高得分
            hiscore = self.loadHiscore()
            # 选择界面的内容
            screen.blit(self.font.render(u"最高得分-" + str(hiscore), True, pygame.Color('white')), [170, 35])
            screen.blit(self.font.render("1 PLAYER", True, pygame.Color('white')), [165, 250])
            screen.blit(self.font.render("2 PLAYERS", True, pygame.Color('white')), [165, 275])
            screen.blit(self.font.render("(c) 1980 1985 NAMCO LTD.", True, pygame.Color('white')), [140, 350])
            screen.blit(self.font.render("ALL RIGHTS RESERVED", True, pygame.Color('white')), [140, 380])

        # 画self.player_image图像到选择界面，接受按键事件来选择单人或多人模式
        if self.nr_of_players == 1:
            screen.blit(self.player_image, [125, 245])
        elif self.nr_of_players == 2:
            screen.blit(self.player_image, [125, 270])

        # 是否立即画选择界面到游戏窗口中
        if put_on_surface:
            pygame.display.flip()

    def animateIntroScreen(self):
        """ 选择菜单从下往上滑动效果 """
        global screen
        # 画选择界面
        self.drawIntroScreen(False)
        # 获取一个screen的拷贝，用于保存选择界面，原界面填充回全黑
        screen_cp = screen.copy()
        screen.fill([0, 0, 0])

        # 画选择界面的y坐标，416表示从游戏窗口最底部开始画，0是最顶部
        y = 416
        while (y > 0):
            time_passed = self.clock.tick(50)
            # 在选择界面从下往上滑动的过程中按回车键，则选择界面立即填满游戏窗口
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        y = 0
                        break
            # 画选择界面到游戏窗口中
            screen.blit(screen_cp, [0, y])
            pygame.display.flip()
            # 选择界面每次上移5像素
            y -= 5

        # 最后把选择界面完全填充到游戏窗口中
        screen.blit(screen_cp, [0, 0])
        pygame.display.flip()

    def chunks(self, l, n):
        """ 将字符串分割成块，n是每块大小 """
        return [l[i:i + n] for i in range(0, len(l), n)]

    def writeInBricks(self, text, pos):
        global screen, sprites

        bricks = sprites.subsurface(56 * 2, 64 * 2, 8 * 2, 8 * 2)
        brick1 = bricks.subsurface((0, 0, 8, 8))
        brick2 = bricks.subsurface((8, 0, 8, 8))
        brick3 = bricks.subsurface((8, 8, 8, 8))
        brick4 = bricks.subsurface((0, 8, 8, 8))

        alphabet = {
            "a": "0071b63c7ff1e3",
            "b": "01fb1e3fd8f1fe",
            "c": "00799e0c18199e",
            "e": "01fb060f98307e",
            "g": "007d860cf8d99f",
            "i": "01f8c183060c7e",
            "l": "0183060c18307e",
            "m": "018fbffffaf1e3",
            "o": "00fb1e3c78f1be",
            "r": "01fb1e3cff3767",
            "t": "01f8c183060c18",
            "v": "018f1e3eef8e08",
            "y": "019b3667860c18"
        }

        abs_x, abs_y = pos

        for letter in text.lower():

            binstr = ""
            for h in self.chunks(alphabet[letter], 2):
                binstr += str(bin(int(h, 16)))[2:].rjust(8, "0")
            binstr = binstr[7:]

            x, y = 0, 0
            letter_w = 0
            surf_letter = pygame.Surface((56, 56))
            for j, row in enumerate(self.chunks(binstr, 7)):
                for i, bit in enumerate(row):
                    if bit == "1":
                        if i % 2 == 0 and j % 2 == 0:
                            surf_letter.blit(brick1, [x, y])
                        elif i % 2 == 1 and j % 2 == 0:
                            surf_letter.blit(brick2, [x, y])
                        elif i % 2 == 1 and j % 2 == 1:
                            surf_letter.blit(brick3, [x, y])
                        elif i % 2 == 0 and j % 2 == 1:
                            surf_letter.blit(brick4, [x, y])
                        if x > letter_w:
                            letter_w = x
                    x += 8
                x = 0
                y += 8
            screen.blit(surf_letter, [abs_x, abs_y])
            abs_x += letter_w + 16

    def toggleEnemyFreeze(self, freeze=True):
        """ 宝物效果，暂停所有敌人 """
        global enemies

        for enemy in enemies:
            enemy.paused = freeze
        self.timefreeze = freeze

    def loadHiscore(self):
        """ 加载游戏得分 """
        filename = ".hiscore"
        # 从文件中加载最高分数，没有则直接返回20000
        if (not os.path.isfile(filename)):
            return 20000

        f = open(filename, "r")
        hiscore = int(f.read().strip())

        if hiscore > 19999 and hiscore < 1000000:
            return hiscore
        else:
            print("cheater =[")
            return 20000

    def saveHiscore(self, hiscore):
        """ 保存游戏得分 """
        try:
            f = open(".hiscore", "w")
            f.write(str(hiscore))
        except:
            print("Can't save hiscore")
            return False
        finally:
            f.close()
        return True

    def finishLevel(self):
        """ 通过这一关，进入下一关 """

        global play_sounds, sounds

        if play_sounds:
            sounds["bg"].stop()

        self.active = False
        gtimer.add(3000, lambda: self.showScores(), 1)

        print("Stage " + str(self.stage) + " completed")

    def nextLevel(self):
        """ 进入下一关 """
        global castle, players, bullets, bonuses, play_sounds, sounds

        del bullets[:]
        del enemies[:]
        del bonuses[:]
        # 画玩家基地
        castle.rebuild()
        del gtimer.timers[:]

        # 加载地形图和标识可以被子弹消灭的障碍物
        self.stage += 1
        self.level = Level(self.stage)
        self.timefreeze = False

        # 每一关四种不同类型的坦克的数量
        levels_enemies = (
            (18, 2, 0, 0), (14, 4, 0, 2), (14, 4, 0, 2), (2, 5, 10, 3), (8, 5, 5, 2),
            (9, 2, 7, 2), (7, 4, 6, 3), (7, 4, 7, 2), (6, 4, 7, 3), (12, 2, 4, 2),
            (5, 5, 4, 6), (0, 6, 8, 6), (0, 8, 8, 4), (0, 4, 10, 6), (0, 2, 10, 8),
            (16, 2, 0, 2), (8, 2, 8, 2), (2, 8, 6, 4), (4, 4, 4, 8), (2, 8, 2, 8),
            (6, 2, 8, 4), (6, 8, 2, 4), (0, 10, 4, 6), (10, 4, 4, 2), (0, 8, 2, 10),
            (4, 6, 4, 6), (2, 8, 2, 8), (15, 2, 2, 1), (0, 4, 10, 6), (4, 8, 4, 4),
            (3, 8, 3, 6), (6, 4, 2, 8), (4, 4, 4, 8), (0, 10, 4, 6), (0, 6, 4, 10),
        )
        # 大于35关的关卡，一律使用第35关的敌方坦克类型
        if self.stage <= 35:
            enemies_l = levels_enemies[self.stage - 1]
        else:
            enemies_l = levels_enemies[34]

        # 打乱四种类型的敌方坦克出战顺序
        self.level.enemies_left = [0] * enemies_l[0] + [1] * enemies_l[1] + [2] * enemies_l[2] + [3] * enemies_l[3]
        random.shuffle(self.level.enemies_left)

        # 开始放游戏声音
        if play_sounds:
            sounds["start"].play()
            gtimer.add(4330, lambda: sounds["bg"].play(-1), 1)

        # 初始化玩家坦克
        self.reloadPlayers()

        # 玩家坦克出现3秒后，出现敌方坦克
        gtimer.add(3000, lambda: self.spawnEnemy())

        # 游戏结束开关
        self.game_over = False

        # 游戏主循环开关
        self.running = True

        self.active = True

        self.draw()

        while self.running:
            time_passed = self.clock.tick(50)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pass
                elif event.type == pygame.QUIT:
                    quit()
                # 按下键盘的一个键触发
                elif event.type == pygame.KEYDOWN and not self.game_over and self.active:
                    # 切换播放声音
                    if event.key == pygame.K_m:
                        play_sounds = not play_sounds
                        if not play_sounds:
                            pygame.mixer.stop()
                        else:
                            sounds["bg"].play(-1)

                    for player in players:
                        if player.state == player.STATE_ALIVE:
                            try:
                                index = player.controls.index(event.key)
                            except:
                                pass
                            else:
                                # 按下空格键，表示开火
                                if index == 0:
                                    if player.fire() and play_sounds:
                                        sounds["fire"].play()
                                # 按下向上键，向上移动
                                elif index == 1:
                                    player.pressed[0] = True
                                # 按下向右键，向右移动
                                elif index == 2:
                                    player.pressed[1] = True
                                # 按下向下键，向下移动
                                elif index == 3:
                                    player.pressed[2] = True
                                # 按下向左键，向左移动
                                elif index == 4:
                                    player.pressed[3] = True
                # 松开按下的键盘键触发
                elif event.type == pygame.KEYUP and not self.game_over and self.active:
                    for player in players:
                        if player.state == player.STATE_ALIVE:
                            try:
                                index = player.controls.index(event.key)
                            except:
                                pass
                            else:
                                # 松开向上键，停止向上移动
                                if index == 1:
                                    player.pressed[0] = False
                                # 松开向右键，停止向右移动
                                elif index == 2:
                                    player.pressed[1] = False
                                # 松开向下键，停止向下移动
                                elif index == 3:
                                    player.pressed[2] = False
                                # 松开向左键，停止向左移动
                                elif index == 4:
                                    player.pressed[3] = False

            OnPlaying.game_running(self, players, enemies, bullets, bonuses)

            # 更新玩家坦克下次出现坐标
            for player in players:
                if player.state == player.STATE_ALIVE and not self.game_over and self.active:
                    if player.pressed[0] == True:
                        player.move(self.DIR_UP)
                    elif player.pressed[1] == True:
                        player.move(self.DIR_RIGHT)
                    elif player.pressed[2] == True:
                        player.move(self.DIR_DOWN)
                    elif player.pressed[3] == True:
                        player.move(self.DIR_LEFT)
                player.update(time_passed)

            for enemy in enemies:
                if enemy.state == enemy.STATE_DEAD and not self.game_over and self.active:
                    enemies.remove(enemy)
                    if len(self.level.enemies_left) == 0 and len(enemies) == 0:
                        self.finishLevel()
                else:
                    enemy.update(time_passed)

            if not self.game_over and self.active:
                for player in players:
                    if player.state == player.STATE_ALIVE:
                        if player.bonus != None and player.side == player.SIDE_PLAYER:
                            # 触发宝物效果
                            self.triggerBonus(bonus, player)
                            player.bonus = None
                    # 命用完就结束，否则产生新的玩家坦克
                    elif player.state == player.STATE_DEAD:
                        self.superpowers = 0
                        player.lives -= 1
                        if player.lives > 0:
                            self.respawnPlayer(player)
                        else:
                            self.gameOver()

            for bullet in bullets:
                if bullet.state == bullet.STATE_REMOVED:
                    bullets.remove(bullet)
                else:
                    bullet.update()

            for bonus in bonuses:
                if bonus.active == False:
                    bonuses.remove(bonus)

            for label in labels:
                if not label.active:
                    labels.remove(label)

            # 玩家基地被击中，游戏结束
            if not self.game_over:
                if not castle.active:
                    self.gameOver()

            gtimer.update(time_passed)

            self.draw()


if __name__ == "__main__":

    # 图像资源
    sprites = None
    # 游戏窗口
    screen = None
    # 玩家坦克
    players = []
    # 敌方坦克
    enemies = []
    # 炮弹
    bullets = []
    # 宝物
    bonuses = []

    labels = []
    # 是否播放声音
    play_sounds = False
    # 所有声音
    sounds = {}

    game = Game()
    castle = Castle()
    # 开始游戏，画选择界面
    game.showMenu()
