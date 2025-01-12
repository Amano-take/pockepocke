import threading, signal
import time
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from game import *
from AI.rulebase_player import RuleBasePlayer


class Visualizer:
    def __init__(self):
        self.game = Game()
        self.stop_event = threading.Event()

    def set_players(self, player1: Player, player2: Player):
        self.game.set_players(player1, player2)

    def visualize(self):
        with open("./interface/visualized.txt", "w") as f:
            while not self.stop_event.is_set():
                f.seek(0)
                f.truncate()
                f.write(str(self.game.player1) + "\n")

                f.write("sides: " + str(self.game.player1.sides) + "\n")
                f.write(
                    "current_energy: " + str(self.game.player1.current_energy) + "\n"
                )
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
                f.write(
                    "current_energy: " + str(self.game.player2.current_energy) + "\n"
                )
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
        def signal_handler(signal, frame):
            self.stop_event.set()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        thread1 = threading.Thread(target=self.game.start, daemon=True)
        thread2 = threading.Thread(target=self.visualize, daemon=True)
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()


if __name__ == "__main__":
    visualizer = Visualizer()
    from tests.utils.set_lightning import lightning_deck

    deck = lightning_deck()

    player1 = Player(Deck(deck), [Energy.LIGHTNING])
    player1.name = "player1"
    player2 = RuleBasePlayer(Deck(deck), [Energy.LIGHTNING])
    player2.name = "rulebase"
    visualizer.set_players(player1, player2)
    visualizer.start()
