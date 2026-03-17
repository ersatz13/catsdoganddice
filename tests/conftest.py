from __future__ import annotations

from game import Bag, Die, Player, build_cat_cards, build_dog_cards


def card_named(name: str, kind: str):
    cards = build_cat_cards() if kind == "cat" else build_dog_cards()
    for card in cards:
        if card.name == name:
            return card
    raise AssertionError(f"Card not found: {kind}:{name}")


def make_player(
    name: str = "Tester",
    *,
    is_ai: bool = False,
    bag: Bag | None = None,
    objective_color: str | None = None,
    dog_names: list[str] | None = None,
    stolen_dog_names: list[str] | None = None,
    temp_dog_names: list[str] | None = None,
    cat_names: list[str] | None = None,
) -> Player:
    player = Player(
        name=name,
        is_ai=is_ai,
        bag=bag or Bag(),
        objective_color=objective_color,
    )
    player.dog_cards = [card_named(card_name, "dog") for card_name in (dog_names or [])]
    player.stolen_dog_cards = [
        card_named(card_name, "dog") for card_name in (stolen_dog_names or [])
    ]
    player.temp_dog_cards = [card_named(card_name, "dog") for card_name in (temp_dog_names or [])]
    player.cat_cards = [card_named(card_name, "cat") for card_name in (cat_names or [])]
    return player


def dice(*items: tuple[str, int]) -> list[Die]:
    return [Die(color, value) for color, value in items]

