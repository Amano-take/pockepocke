from game.cards.pockemon_card import PockemonCard
from game.cards.pockemon_cards.grass_cards import *
from game.cards.pockemon_cards.lightning_card import *
from game.cards.pockemon_cards.psycic_cards import *
from game.cards.goods_cards.goods import *
from game.cards.trainer_cards.trainers import *
from game.cards.base_card import Card
from game.cards.trainer_cards.trainers import TrainerCard
from game.cards.goods_cards.goods import GoodsCard


# カードの種類ごとのリスト
POKEMON_CARDS: list[type[PockemonCard]] = GRASS_CARDS + LIGHTNING_CARDS + PSYCHIC_CARDS
ALL_CARDS: list[type[PockemonCard] | type[TrainerCard] | type[GoodsCard]] = (
    POKEMON_CARDS + GOODS_CARDS + TRAINER_CARDS
)
