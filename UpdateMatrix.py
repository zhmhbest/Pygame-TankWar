
# 地形常量
(TILE_EMPTY, TILE_BRICK, TILE_STEEL, TILE_WATER, TILE_GRASS, TILE_FROZE) = range(6)

# 地形像素尺寸
TILE_SIZE = 16


def tank_position(tank):
    return mapping(tank.rect.top, tank.rect.left)


def update_map(map_matrix, players, enemies, bullets, mapr):
    clear_map(map_matrix)
    update_map_player(map_matrix, players)
    update_map_enemy(map_matrix, enemies)
    update_map_bullet(map_matrix, bullets)
    update_map_wall(map_matrix, mapr)


def mapping(x, y):
    return x // TILE_SIZE, y // TILE_SIZE


def clear_map(map_matrix):
    for i in range(map_matrix.__len__()):
        for j in range(map_matrix[i].__len__()):
            map_matrix[i][j] = -1
    # for row in map_matrix:
    #     print(row)


def update_map_wall(map_matrix, mapr):
    for item in mapr:
        pos = mapping(item[1].top, item[1].left)
        map_matrix[pos[0]][pos[1]] = item[0]


def update_map_tank(map_matrix, tank, t):
    pos1 = mapping(tank.rect.top, tank.rect.left)
    map_matrix[pos1[0]][pos1[1]] = 50 + t
    map_matrix[pos1[0]+1][pos1[1]+1] = 50 + t
    map_matrix[pos1[0]][pos1[1]+1] = 50 + t
    map_matrix[pos1[0]+1][pos1[1]] = 50 + t


def update_map_player(map_matrix, players):
    update_map_tank(map_matrix, players[0], 1)
    if 2 == len(players):
        update_map_tank(map_matrix, players[1], 2)


def update_map_enemy(map_matrix, enemies):
    for enemy in enemies:
        update_map_tank(map_matrix, enemy, 3)


def update_map_bullet(map_matrix, bullets):
    for bullet in bullets:
        pos = mapping(bullet.rect.top, bullet.rect.left)
        try:
            map_matrix[pos[0]][pos[1]] = 61
        except IndexError:
            pass


def print_map(map_matrix):
    for row in map_matrix:
        for col in row:
            if col == TILE_BRICK:
                print("#", end='')
            elif col == TILE_STEEL:
                print("@", end='')
            elif col == TILE_WATER:
                print("~", end='')
            elif col == TILE_GRASS:
                print("%", end='')
            elif col == TILE_FROZE:
                print("-", end='')
            elif col == 51:
                print("1", end='')
            elif col == 52:
                print("2", end='')
            elif col == 53:
                print("T", end='')
            elif col == 61:
                print("^", end='')
            else:
                print('.', end='')
        print()

