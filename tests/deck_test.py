import pytest
from game.cards.pockemon_cards.grass_cards import (
    TamaTama,
    Nassy,
    Selevi,
    Tsutaja,
    Janobii,
    Jaroda,
    Nemashu,
    Masheedo,
    Dadarin,
)
from game.deck import Deck


def test_init_deck():
    deck_list = []
    deck_list.append(TamaTama())
    for _ in range(19):
        deck_list.append(Nassy())

    deck = Deck(deck_list)
    deck.init_deck()
    flag = False
    for _ in range(5):
        card = deck.draw()
        if isinstance(card, TamaTama):
            flag = True
            break
    assert flag == True


if __name__ == "__main__":
    deck_draw_test()
    print("deck_draw_test passed")
