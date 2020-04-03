
from UpdateMatrix import tank_position, update_map, print_map
from Player1 import main as player1_main
from CommonHeader import STATE_ALIVE


class OnPlaying:
    game = None

    @staticmethod
    def game_running(players, enemies, bullets, bonuses):
        map_matrix = OnPlaying.game.level.map_matrix
        update_map(
            map_matrix,
            players,
            enemies,
            bullets,
            OnPlaying.game.level.mapr
        )

        # print_map(map_matrix)

        player1 = players[0]
        if player1.state == STATE_ALIVE:
            player1_main(player1, tank_position(player1))

        # if 2 == len(players):
        #     player2 = players[1]
        #     if player2.state == STATE_ALIVE:
        #         player2_main(player2, tank_position(player2))
