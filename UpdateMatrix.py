
# 地形常量
(TILE_EMPTY, TILE_BRICK, TILE_STEEL, TILE_WATER, TILE_GRASS, TILE_FROZE) = range(6)

# 地形像素尺寸
TILE_SIZE = 16


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


def update_map_player(map_matrix, players):
    player = players[0]
    pos = mapping(player.rect.top, player.rect.left)
    map_matrix[pos[0]][pos[1]] = 51
    if 2 == len(players):
        player = players[1]
        pos = mapping(player.rect.top, player.rect.left)
        map_matrix[pos[0]][pos[1]] = 52


def update_map_enemy(map_matrix, enemies):
    for enemy in enemies:
        pos = mapping(enemy.rect.top, enemy.rect.left)
        map_matrix[pos[0]][pos[1]] = 53


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
            else:
                print('.', end='')
        print()

