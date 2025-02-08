from game.cards import (
    GRASS_CARDS,
    LIGHTNING_CARDS,
    PSYCHIC_CARDS,
    GOODS_CARDS,
    TRAINER_CARDS,
    POKEMON_CARDS,
    ALL_CARDS,
)
from game.cards.pockemon_card import PockemonCard
from game.cards.goods_cards.goods import GoodsCard
from game.cards.trainer_cards.trainers import TrainerCard


def test_card_lists_not_empty():
    """各カードリストが空でないことを確認"""
    assert len(GRASS_CARDS) > 0
    assert len(LIGHTNING_CARDS) > 0
    assert len(PSYCHIC_CARDS) > 0
    assert len(GOODS_CARDS) > 0
    assert len(TRAINER_CARDS) > 0


def test_pokemon_cards_aggregation():
    """POKEMONカードの集約が正しいことを確認"""
    expected_length = len(GRASS_CARDS) + len(LIGHTNING_CARDS) + len(PSYCHIC_CARDS)
    assert len(POKEMON_CARDS) == expected_length


def test_all_cards_aggregation():
    """全カードの集約が正しいことを確認"""
    expected_length = len(POKEMON_CARDS) + len(GOODS_CARDS) + len(TRAINER_CARDS)
    assert len(ALL_CARDS) == expected_length


def test_card_types():
    """各カードが正しい型であることを確認"""
    # ポケモンカード
    for card_class in POKEMON_CARDS:
        card = card_class()
        assert isinstance(card, PockemonCard)

    # グッズカード
    for card_class in GOODS_CARDS:
        card = card_class()
        assert isinstance(card, GoodsCard)

    # トレーナーカード
    for card_class in TRAINER_CARDS:
        card = card_class()
        assert isinstance(card, TrainerCard)


def test_card_uniqueness():
    """カードの重複がないことを確認"""
    card_names = set()
    for card_class in ALL_CARDS:
        card = card_class()
        assert card.name not in card_names, f"Duplicate card found: {card.name}"
        card_names.add(card.name)


def test_basic_pokemon_existence():
    """種ポケモンが存在することを確認"""
    has_basic_pokemon = False
    for card_class in POKEMON_CARDS:
        card = card_class()
        if hasattr(card, "is_seed") and card.is_seed:
            has_basic_pokemon = True
            break
    assert has_basic_pokemon, "No basic pokemon found"
