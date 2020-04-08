# AI博弈平台——坦克大战

- [参考源码](http://battle-city-tanks.googlecode.com/files/tanks_v1.0.zip)

## 环境与启动

需要安装pygame，运行BattleCity.py启动游戏。

## 运行加速

```python
PlayEnhance.accelerate(num)
# num: 0~100
```

## 编写须知

- 玩家1在`Player1.py: main`下编写代码
- 玩家2在`Player2.py: main`下编写代码

### 地图信息

```python
PlayEnhance.get_map()
PlayEnhance.get_map_size()
```
该量是一个二维数组，描绘了当前地图的主要信息。



```
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
```

使用`PlayEnhance.get_map()[i][j] == TYPE`来判断一个像素的具体信息
`TYPE`的取值可以是（详见`CommonHeader.py`）：

- TILE_BRICK:    砖块
- TILE_STEEL:    铁
- TILE_WATER:    水
- ILE_GRASS:     草
- TILE_FROZE:    冰
- TANK_PLAYER1:  玩家1
- TANK_PLAYER2:  玩家2
- TANK_PLAYER3:  敌人
- TANK_BULLET :  子弹

```python
PlayEnhance.print_map()
```
该方法打印一个人可以看懂的地图信息，注意这个只能阅读，并非地图内的真实值。

### 坦克相关操作

特别注意，如果被障碍物阻挡，移动操作可能无效。

- `tank.go_up()`
- `tank.go_down()`
- `tank.go_left()`
- `tank.go_right()`
- `tank.fire()`
- `tank.score` 当前玩家得分
- `tank.lives` 当前玩家剩余血量
- `tank.direction` 当前开火方向（状态码详见`CommonHeader.py`）
- `position` 本人所在坐标，一个元组

```python
# 获取敌军坦克坐标
PlayEnhance.get_position(enemy_tank)
```

```python
# 获取所有敌军坦克
PlayEnhance.get_all_enemies()
```

### 高级功能

该部分是一些常用功能，用来简化同学们的编写代码量，
算法可能不够完善，有高级需求的同学，请在自己的文件另行改写。

```python
# 返回元素在地图上的坐标以及元素本身（地形元素返回坐标和None）
PlayEnhance.find_element(tank, direction, value_type)
```

```python
# 获取敌军坦克当前朝向
PlayEnhance.find_enemy_towards(tank, direction)
```

```python
# 依据坐标找到对应对象
PlayEnhance.mapping_coordinate_to_object(x, y, value_type)
```
