import threading
import time
from game import *


class Visualizer:
    def __init__(self):
        self.game = Game()

    def set_players(self, player1: Player, player2: Player):
        self.game.set_players(player1, player2)

    def visualize(self):
        with open("./interface/visualized.txt", "w") as f:
            while True:
                f.seek(0)
                f.truncate()
                f.write(str(self.game.player1) + "\n")

                f.write("sides: " + str(self.game.player1.sides) + "\n")
                f.write("current_energy: " + str(self.game.player1.current_energy) + "\n")
                f.write("energy_value: " + str(self.game.player1.energy_values) + "\n")
                f.write(
                    "hand: "
                    + str(self.game.player1.hand_goods)
                    + ", "
                    + str(self.game.player1.hand_pockemon)
                    + ", "
                    + str(self.game.player1.hand_trainer)
                    + "\n"
                )
                f.write("bench: " + str(self.game.player1.bench) + "\n")
                f.write("active: " + str(self.game.player1.active_pockemon) + "\n")

                f.write("--------------------\n")
                f.write(str(self.game.player2) + "\n")
                f.write("sides: " + str(self.game.player2.sides) + "\n")
                f.write("current_energy: " + str(self.game.player2.current_energy) + "\n")
                f.write("energy_value: " + str(self.game.player2.energy_values) + "\n")
                f.write(
                    "hand: "
                    + str(self.game.player2.hand_goods)
                    + ", "
                    + str(self.game.player2.hand_pockemon)
                    + ", "
                    + str(self.game.player2.hand_trainer)
                    + "\n"
                )
                f.write("bench: " + str(self.game.player2.bench) + "\n")
                f.write("active: " + str(self.game.player2.active_pockemon) + "\n")

                f.flush()
                time.sleep(1)

    def start(self):
        thread1 = threading.Thread(target=self.game.start)
        thread2 = threading.Thread(target=self.visualize)
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()


if __name__ == "__main__":
    visualizer = Visualizer()
    deck = [
        TamaTama(),
        Nassy(),
        Selevi(),
        MonsterBall(),
        MonsterBall(),
        KizuGusuri(),
        KizuGusuri(),
        Speeder(),
        Speeder(),
        RedCard(),
    ]
    for _ in range(20 - len(deck)):
        deck.append(Tsutaja())

    player1 = Player(Deck(deck), [Energy.GRASS])
    player2 = Player(Deck(deck), [Energy.FIRE])

    visualizer.set_players(player1, player2)
    visualizer.start()
