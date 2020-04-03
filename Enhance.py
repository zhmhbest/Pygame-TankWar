from CommonHeader import *
from UpdateMatrix import tank_position, mapping



class PlayEnhance:
    game = None
    enemies = None
    bullets = None

    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

    @staticmethod
    def get_map() -> list:
        return PlayEnhance.game.level.map_matrix

    @staticmethod
    def print_map():
        from UpdateMatrix import print_map as pm
        pm(PlayEnhance.game.level.map_matrix)

    @staticmethod
    def get_position(tank):
        return tank_position(tank)

    @staticmethod
    def get_all_enemies() -> list:
        return PlayEnhance.enemies

    @staticmethod
    def get_map_size() -> (int, int):
        row = len(PlayEnhance.get_map())
        col = len(PlayEnhance.get_map()[0])
        return row, col

    # ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■

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
            groups = PlayEnhance.enemies
        elif value_type == TANK_BULLET:
            groups = PlayEnhance.bullets
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
        map_matrix = PlayEnhance.get_map()
        elems = []
        if direction == DIR_UP:
            while x >= 0:
                if map_matrix[x][y] == value_type:
                    item = PlayEnhance.mapping_coordinate_to_object(x, y, value_type)
                    elems.append((x, y, item))
                    x -= 1
                x -= 1

        if direction == DIR_DOWN:
            while x < PlayEnhance.get_map_size()[0]:
                if map_matrix[x][y] == value_type:
                    item = PlayEnhance.mapping_coordinate_to_object(x, y, value_type)
                    elems.append((x, y, item))
                    x += 1
                x += 1

        if direction == DIR_LEFT:
            while y >= 0:
                if map_matrix[x][y] == value_type:
                    item = PlayEnhance.mapping_coordinate_to_object(x, y, value_type)
                    elems.append((x, y, item))
                    y -= 1
                y -= 1

        if direction == DIR_RIGHT:
            while y < PlayEnhance.get_map_size()[1]:
                if map_matrix[x][y] == value_type:
                    item = PlayEnhance.mapping_coordinate_to_object(x, y, value_type)
                    elems.append((x, y, item))
                    y += 1
                y += 1

        return elems

    @staticmethod
    def find_enemy_towards(tank, direction):
        return PlayEnhance.find_element(tank, direction, TANK_PLAYER3)
