from game import build_dog_modifiers

from tests.conftest import make_player


def test_daredevil_doubles_plus_one_modifiers_including_stolen_dogs() -> None:
    player = make_player(
        dog_names=["Daredevil Dawg", "Barrel Dawg"],
        stolen_dog_names=["Tri-tail Dawg"],
        temp_dog_names=["Diamond Dawg"],
    )
    mods = build_dog_modifiers(player)
    assert mods.pair_bonus == 2
    assert mods.three_kind_bonus == 2
    assert mods.five_kind_bonus == 2


def test_alpha_dawg_discount_is_doubled_by_daredevil() -> None:
    from game import Game

    player = make_player(dog_names=["Alpha Dawg", "Daredevil Dawg"])
    game = Game([player])
    target = next(card for card in game.dog_deck._base if card.name == "Service Dawg")
    assert game.dog_card_cost(player, target) == 2


def test_cats_best_friend_increases_cat_limit() -> None:
    from game import Game

    player = make_player(dog_names=["Cats Best Friend", "Cats Best Friend"])
    game = Game([player], max_cat_cards=2)
    assert game.max_cat_limit(player) == 4


def test_blocked_dog_is_ignored_by_modifiers() -> None:
    barrel = make_player(dog_names=["Barrel Dawg"]).dog_cards[0]
    player = make_player()
    player.dog_cards = [barrel]
    player.blocked_dog_card = barrel
    player.blocked_dog_active = True
    mods = build_dog_modifiers(player)
    assert mods.pair_bonus == 0

