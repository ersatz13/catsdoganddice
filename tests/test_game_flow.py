import random

from game import Bag, Game

from tests.conftest import card_named, dice, make_player


def test_start_turn_rolls_five_dice_by_default() -> None:
    player = make_player(bag=Bag({"red": 5, "blue": 5, "yellow": 5, "green": 5, "purple": 5}))
    game = Game([player])
    random.seed(1)
    game.start_turn(player)
    assert len(game.current_hand) == 5
    assert game.rerolls_left == 2


def test_start_turn_applies_roll_bonus_and_penalty_bounds() -> None:
    player = make_player(bag=Bag({"red": 20, "blue": 20, "yellow": 20, "green": 20, "purple": 20}))
    player.pending_roll_bonus = 4
    player.pending_roll_penalty = 3
    player.pending_roll_penalty_round = 1
    game = Game([player])
    random.seed(2)
    game.start_turn(player)
    assert len(game.current_hand) == 6


def test_wheres_rufus_forces_objective_die_on_first_roll() -> None:
    player = make_player(
        bag=Bag({"red": 5, "blue": 5, "yellow": 5, "green": 5, "purple": 0}),
        objective_color="red",
        dog_names=["Where's Rufus"],
    )
    game = Game([player])
    random.seed(3)
    game.start_turn(player)
    assert any(die.color == "red" for die in game.current_hand)


def test_full_reroll_with_bull_dawg_grants_extra_reroll_once() -> None:
    player = make_player(
        bag=Bag({"red": 10, "blue": 10, "yellow": 10, "green": 10, "purple": 10}),
        dog_names=["Bull Dawg"],
    )
    game = Game([player])
    random.seed(4)
    game.start_turn(player)
    assert game.rerolls_left == 2
    game.reroll(player, [0, 1, 2, 3, 4])
    assert game.rerolls_left == 2
    game.reroll(player, [0, 1, 2, 3, 4])
    assert game.rerolls_left == 1


def test_nimble_rerolls_keep_hand_size_and_do_not_set_aside_dice() -> None:
    player = make_player(
        bag=Bag({"red": 10, "blue": 10, "yellow": 10, "green": 10, "purple": 10}),
    )
    player.pending_nimble_dice = 2
    game = Game([player])
    random.seed(5)
    game.start_turn(player)
    before = list(game.current_hand)
    rerolled = game.reroll(player, [0, 1])
    assert len(game.current_hand) == 5
    assert len(game.set_aside) == 0
    assert rerolled == [0, 1]
    assert game.current_hand[0] != before[0] or game.current_hand[1] != before[1]


def test_finish_turn_returns_dice_to_bag_and_clears_hand() -> None:
    player = make_player(bag=Bag({"red": 5, "blue": 5, "yellow": 5, "green": 5, "purple": 5}))
    game = Game([player])
    random.seed(6)
    game.start_turn(player)
    total_before = player.bag.total()
    game.finish_turn(player)
    assert game.current_hand == []
    assert game.set_aside == []
    assert player.bag.total() == total_before + 5


def test_buy_card_uses_free_dog_claim_before_spending_kibbles() -> None:
    player = make_player()
    player.kibbles = 0
    player.free_dog_claims = 1
    game = Game([player])
    dog = card_named("Service Dawg", "dog")
    assert game.can_buy(player, dog) is True
