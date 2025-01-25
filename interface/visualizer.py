import os
import signal
import sys
import threading
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import random

from AI.rulebase_player import RuleBasePlayer
from game import *


class Visualizer:
    def __init__(self):
        self.game = Game()
        self.stop_event = threading.Event()
        # set random seed
        random.seed(0)

    def set_players(self, player1: Player, player2: Player):
        self.game.set_players(player1, player2)

    def visualize(self):
        with open("./interface/visualized.txt", "w", encoding="utf-8") as f:
            while not self.stop_event.is_set():
                f.seek(0)
                f.truncate()

                # Display turn and game state
                border = "╔" + "═" * 48 + "╗\n"
                f.write(border)
                turn_text = f"Turn {self.game.turn}"
                padding = (48 - len(turn_text)) // 2
                f.write(
                    "║"
                    + " " * padding
                    + turn_text
                    + " " * (48 - padding - len(turn_text))
                    + "║\n"
                )
                f.write("╚" + "═" * 48 + "╝\n\n")

                # Helper function to create HP bar
                def create_hp_bar(pokemon):
                    bar_length = 20
                    filled = int((pokemon.hp / pokemon.max_hp) * bar_length)
                    hp_bar = "█" * filled + "░" * (bar_length - filled)
                    return f"{pokemon.hp}/{pokemon.max_hp} {hp_bar}"

                # Helper function to create energy display
                def create_energy_display(energies):
                    energy_symbols = {
                        "LIGHTNING": "雷",
                        "FIRE": "火",
                        "WATER": "水",
                        "GRASS": "草",
                        "PSYCHIC": "超",
                        "FIGHTING": "闘",
                    }
                    energy_list = []
                    for i, count in enumerate(energies.energies):
                        if count > 0:
                            symbol = energy_symbols.get(str(Energy(i)), "無")
                            energy_list.extend([symbol] * count)
                    return "".join(energy_list)

                # Player 1 display
                f.write(f"PLAYER 1: {self.game.player1}\n")
                f.write(f"Prize Cards: {'🎴' * self.game.player1.sides}\n")

                # Active Pokemon display
                f.write("Active Pokemon:\n")
                if self.game.player1.active_pockemon:
                    pokemon = self.game.player1.active_pockemon
                    hp_bar = create_hp_bar(pokemon)
                    energy_display = create_energy_display(pokemon.energies)
                    f.write(
                        f"  {pokemon.name} "
                        + " " * (20 - len(pokemon.name))
                        + f"HP:[{hp_bar}] {energy_display}\n"
                    )
                else:
                    f.write("  None\n")

                # Bench display
                f.write("Bench:\n")
                for i, pokemon in enumerate(self.game.player1.bench):
                    hp_bar = create_hp_bar(pokemon)
                    energy_display = create_energy_display(pokemon.energies)
                    f.write(
                        f"  {i+1}. {pokemon.name} "
                        + " " * (18 - len(pokemon.name))
                        + f"HP:[{hp_bar}] {energy_display}\n"
                    )

                # Hand cards display
                f.write("Hand:\n")
                if self.game.player1.hand_pockemon:
                    f.write(
                        "  Pokemon: "
                        + ", ".join([p.name for p in self.game.player1.hand_pockemon])
                        + "\n"
                    )
                if self.game.player1.hand_goods:
                    f.write(
                        "  Goods: "
                        + ", ".join([g.name for g in self.game.player1.hand_goods])
                        + "\n"
                    )
                if self.game.player1.hand_trainer:
                    f.write(
                        "  Trainer: "
                        + ", ".join([t.name for t in self.game.player1.hand_trainer])
                        + "\n"
                    )
                f.write("\n")

                # Divider between players
                f.write(" " * 20 + "VS" + " " * 20 + "\n\n")

                # Player 2 display
                f.write(f"PLAYER 2: {self.game.player2}\n")
                f.write(f"Prize Cards: {'🎴' * self.game.player2.sides}\n")

                # Active Pokemon display
                f.write("Active Pokemon:\n")
                if self.game.player2.active_pockemon:
                    pokemon = self.game.player2.active_pockemon
                    hp_bar = create_hp_bar(pokemon)
                    energy_display = create_energy_display(pokemon.energies)
                    f.write(
                        f"  {pokemon.name} "
                        + " " * (20 - len(pokemon.name))
                        + f"HP:[{hp_bar}] {energy_display}\n"
                    )
                else:
                    f.write("  None\n")

                # Bench display
                f.write("Bench:\n")
                for i, pokemon in enumerate(self.game.player2.bench):
                    hp_bar = create_hp_bar(pokemon)
                    energy_display = create_energy_display(pokemon.energies)
                    f.write(
                        f"  {i+1}. {pokemon.name} "
                        + " " * (18 - len(pokemon.name))
                        + f"HP:[{hp_bar}] {energy_display}\n"
                    )

                # Hand cards display
                f.write("Hand:\n")
                if self.game.player2.hand_pockemon:
                    f.write(
                        "  Pokemon: "
                        + ", ".join([p.name for p in self.game.player2.hand_pockemon])
                        + "\n"
                    )
                if self.game.player2.hand_goods:
                    f.write(
                        "  Goods: "
                        + ", ".join([g.name for g in self.game.player2.hand_goods])
                        + "\n"
                    )
                if self.game.player2.hand_trainer:
                    f.write(
                        "  Trainer: "
                        + ", ".join([t.name for t in self.game.player2.hand_trainer])
                        + "\n"
                    )
                f.write("\n")
                f.flush()
                time.sleep(1)

    def start(self):
        def signal_handler(signal, frame):
            self.stop_event.set()
            sys.exit(0)

        def run_game():
            try:
                self.game.start()
            except Exception as e:
                print(f"Error in game thread: {str(e)}")
                # show traceback
                import traceback

                traceback.print_exc()
                self.stop_event.set()
                sys.exit(1)

        signal.signal(signal.SIGINT, signal_handler)
        thread1 = threading.Thread(target=run_game, daemon=True)
        thread2 = threading.Thread(target=self.visualize, daemon=True)
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()


if __name__ == "__main__":
    visualizer = Visualizer()
    from tests.utils.set_lightning import lightning_deck

    deck = lightning_deck()

    player1 = RuleBasePlayer(Deck(deck), [Energy.LIGHTNING])
    player1.name = "rulebase1"
    player2 = RuleBasePlayer(Deck(deck), [Energy.LIGHTNING])
    player2.name = "rulebase2"
    visualizer.set_players(player1, player2)
    visualizer.start()
