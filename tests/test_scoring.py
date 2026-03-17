from game import DogModifiers, best_score, score_five, score_five_with_overrides

from tests.conftest import dice, make_player


def test_score_five_large_straight_base_score() -> None:
    result = score_five(
        dice(
            ("red", 2),
            ("blue", 3),
            ("yellow", 4),
            ("green", 5),
            ("purple", 6),
        ),
        DogModifiers(),
    )
    assert result.name == "Large straight"
    assert result.score == 5
    assert result.color_bonus == 0
    assert result.total == 5


def test_score_five_all_same_color_adds_color_bonus() -> None:
    result = score_five(
        dice(
            ("red", 2),
            ("red", 2),
            ("red", 2),
            ("red", 5),
            ("red", 6),
        ),
        DogModifiers(),
    )
    assert result.name == "Three of a kind"
    assert result.score == 2
    assert result.color_bonus == 1
    assert result.all_same_color is True
    assert result.total == 3


def test_score_five_objective_color_scores_per_matching_die() -> None:
    mods = DogModifiers(objective_color="red")
    result = score_five(
        dice(
            ("red", 2),
            ("red", 2),
            ("red", 5),
            ("blue", 5),
            ("green", 6),
        ),
        mods,
    )
    assert result.name == "Two pair"
    assert result.score == 5
    assert result.total == 5


def test_score_five_service_dawg_turns_no_score_into_points() -> None:
    mods = DogModifiers(no_score_bonus=1)
    result = score_five(
        dice(
            ("red", 1),
            ("blue", 2),
            ("yellow", 4),
            ("green", 5),
            ("purple", 6),
        ),
        mods,
    )
    assert result.name == "No score"
    assert result.score == 0
    assert result.extra_points == 8
    assert result.total == 8


def test_score_five_pit_baws_forces_zero_even_with_good_hand() -> None:
    mods = DogModifiers(force_zero=True, no_score_bonus=1)
    result = score_five(
        dice(
            ("red", 6),
            ("blue", 6),
            ("yellow", 6),
            ("green", 6),
            ("purple", 6),
        ),
        mods,
    )
    assert result.name == "No score"
    assert result.score == 0
    assert result.extra_points == 8
    assert result.total == 8


def test_best_score_picks_best_five_from_six_dice() -> None:
    player = make_player()
    result = best_score(
        dice(
            ("red", 1),
            ("blue", 2),
            ("yellow", 3),
            ("green", 4),
            ("purple", 5),
            ("red", 5),
        ),
        player,
    )
    assert result.name == "Large straight"
    assert result.total == 5
    assert len(result.dice) == 5


def test_starlight_value_wild_can_upgrade_hand() -> None:
    player = make_player()
    hand = dice(
        ("purple", 1),
        ("red", 2),
        ("blue", 2),
        ("green", 2),
        ("yellow", 5),
    )
    wild_ids = {id(hand[0])}
    result = best_score(hand, player, value_wild_ids=wild_ids)
    assert result.name == "Four of a kind"
    assert result.total == 6
    assert result.value_overrides is not None
    assert result.value_overrides[id(hand[0])] == 2


def test_focus_color_override_affects_objective_bonus() -> None:
    player = make_player(objective_color="red")
    hand = dice(
        ("blue", 2),
        ("red", 2),
        ("yellow", 5),
        ("green", 5),
        ("purple", 6),
    )
    result_without = best_score(hand, player)
    result_with = score_five_with_overrides(
        hand,
        DogModifiers(objective_color="red"),
        color_overrides={id(hand[0]): "red"},
    )
    assert result_with.total == result_without.total + 1
