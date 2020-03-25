from BattleCity import Player
from UpdateMatrix import \
    mapping, \
    clear_map, \
    update_map_wall, \
    update_map_player, \
    update_map_enemy, \
    update_map_bullet, \
    print_map

"""
    操作说明
    玩家
        移动
            tank.go_up()
            tank.go_down()
            tank.go_left()
            tank.go_right()
            
        开火
            tank.fire()
        状态: 得分 血量
            print(tank.score)
            print(tank.lives)
        位置
            tank_position(tank)
        朝向
            tank.direction
    
    地图说明：
    
        地图由不同的值组成的二维数组，所以元素对象的坐标也对应的是相应的坐标
        

(0,0)  
    ------------------------->   col(y)
    |
    |                   
    |                     
    |       o--
    |       |__|
    |
    |
    |
    \/
    row（x）
    
    
    TILE_BRICK:    砖块
    TILE_STEEL:    铁
    TILE_WATER:    水
    ILE_GRASS:     草
    TILE_FROZE:    冰
    TANK_PLAYER1:  玩家1
    TANK_PLAYER2:  玩家2
    TANK_PLAYER3:  敌人
    TANK_BULLET :  子弹




"""

# 地形
(TILE_EMPTY, TILE_BRICK, TILE_STEEL, TILE_WATER, TILE_GRASS, TILE_FROZE) = range(6)
# 方向
(DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_LEFT) = range(4)
# 坦克状态
(STATE_SPAWNING, STATE_DEAD, STATE_ALIVE, STATE_EXPLODING) = range(4)

# 玩家
TANK_PLAYER1 = 51
TANK_PLAYER2 = 52
TANK_PLAYER3 = 53

# 子弹
TANK_BULLET = 61


def tank_position(tank):
    return mapping(tank.rect.top, tank.rect.left)


class OnPlaying:
    game = None
    enmies = None
    bullets = None

    @staticmethod
    def game_running(players, enemies, bullets, bonuses):
        clear_map(OnPlaying.game.level.map_matrix)
        update_map_player(OnPlaying.game.level.map_matrix, players)
        update_map_enemy(OnPlaying.game.level.map_matrix, enemies)
        update_map_bullet(OnPlaying.game.level.map_matrix, bullets)
        update_map_wall(OnPlaying.game.level.map_matrix, OnPlaying.game.level.mapr)

        print_map(OnPlaying.game.level.map_matrix)
        player1 = players[0]
        if player1.state == STATE_ALIVE:
            OnPlaying.player_here1(player1, OnPlaying.get_map())
        if 2 == len(players):
            player2 = players[0]
            if player2.state == STATE_ALIVE:
                OnPlaying.player_here2(player2, OnPlaying.get_map())

    @staticmethod
    def get_map() -> list:
        return OnPlaying.game.level.map_matrix

    @staticmethod
    def get_all_enemies() -> list:
        return OnPlaying.enmies

    @staticmethod
    def get_map_size() -> (int, int):
        row = len(OnPlaying.get_map())
        col = len(OnPlaying.get_map()[0])
        return (row, col)

    @staticmethod
    def find_enemy_towards(tank, direction):
        return OnPlaying.find_element(tank, direction, TANK_PLAYER3)

    @staticmethod
    def mapping_coordinate_to_object(x, y, value_type):
        """
        依据坐标找到对应对象
        :param x:
        :param y:
        :param value_type:
        :return:
        """
        groups = None
        if value_type == TANK_PLAYER3:
            groups = OnPlaying.enmies
        elif value_type == TANK_BULLET:
            groups = OnPlaying.bullets
        else:
            return None

        for item in groups:
            item_x, item_y = mapping(item.rect.top, item.rect.left)
            if 0 <= x - item_x <= 1 and 0 <= y - item_y <= 1:
                return item
        return None

    @staticmethod
    def find_element(tank, direction, value_type):
        """

        :param tank:
        :param direction: 搜索方向
        :param value_type: 搜索对象类型（敌人、子弹、地形）
        :rtype :tuple(int, int, value_type_object|None)
        :return: 返回元素在地图上的坐标以及元素本身（地形元素返回坐标和None）
        """
        x, y = tank_position(tank)
        map_matrix = OnPlaying.get_map()
        elem = []
        if direction == DIR_UP:
            while x >= 0:
                if map_matrix[x][y] == value_type:
                    item = OnPlaying.mapping_coordinate_to_object(x,y, value_type)
                    elem.append((x, y,item))
                    x-=1
                x -= 1

        if direction == DIR_DOWN:
            while x < OnPlaying.get_map_size()[0]:
                if map_matrix[x][y] == value_type:
                    item = OnPlaying.mapping_coordinate_to_object(x, y,value_type)
                    elem.append((x, y, item))
                    x+=1
                x += 1

        if direction == DIR_LEFT:
            while y >= 0:
                if map_matrix[x][y] == value_type:
                    item = OnPlaying.mapping_coordinate_to_object(x, y,value_type)
                    elem.append((x, y, item))
                    y-=1
                y -= 1

        if direction == DIR_RIGHT:
            while y < OnPlaying.get_map_size()[1]:
                if map_matrix[x][y] == value_type:
                    item = OnPlaying.mapping_coordinate_to_object(x, y,value_type)
                    elem.append((x, y, item))
                    y+=1
                y += 1

        return elem

    @staticmethod
    def player_here1(tank: Player, map_matrix):
        """
        玩家1 在此游戏
        """
        print("玩家1", tank_position(tank))

        # demo

        # get my direciton
        direction = tank.direction

        # get my position
        x, y = tank_position(tank)

        # search enemy towards
        enemies = OnPlaying.find_enemy_towards(tank, direction)
        if len(enemies) != 0:
            tank.fire()

        for enemy in OnPlaying.get_all_enemies():
            print(tank_position(enemy))

        # search buttlets from north
        bullets = OnPlaying.find_element(tank, DIR_UP, TANK_BULLET)
        for bullet in bullets:
            if bullet[2].direction == DIR_DOWN:
                tank.go_left()




    @staticmethod
    def player_here2(tank: Player, map_matrix):
        """
        玩家2 在此游戏
        """
        print("玩家2", tank_position(tank))
