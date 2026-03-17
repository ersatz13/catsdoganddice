import itertools
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

BASE_COLORS = ["red", "blue", "yellow", "green"]
COLORS = BASE_COLORS + ["purple"]


@dataclass(frozen=True)
class Die:
    color: str
    value: int


class Bag:
    def __init__(self, counts: Optional[Dict[str, int]] = None) -> None:
        self.counts: Dict[str, int] = {c: 0 for c in COLORS}
        if counts:
            for color, count in counts.items():
                self.counts[color] = count

    def total(self) -> int:
        return sum(self.counts.values())

    def draw(self, n: int) -> List[str]:
        drawn: List[str] = []
        for _ in range(n):
            if self.total() <= 0:
                break
            colors, weights = zip(*[(c, self.counts[c]) for c in COLORS if self.counts[c] > 0])
            color = random.choices(colors, weights=weights, k=1)[0]
            self.counts[color] -= 1
            drawn.append(color)
        return drawn

    def remove_random(self, n: int) -> List[str]:
        removed: List[str] = []
        for _ in range(n):
            if self.total() <= 0:
                break
            colors, weights = zip(*[(c, self.counts[c]) for c in COLORS if self.counts[c] > 0])
            color = random.choices(colors, weights=weights, k=1)[0]
            self.counts[color] -= 1
            removed.append(color)
        return removed

    def add(self, color: str, count: int = 1) -> None:
        if color not in self.counts:
            return
        self.counts[color] += max(0, count)

    def recolor(self, from_color: str, to_color: str, count: int = 1) -> int:
        if from_color not in self.counts or to_color not in self.counts:
            return 0
        actual = min(count, self.counts[from_color])
        self.counts[from_color] -= actual
        self.counts[to_color] += actual
        return actual

    def convert_any_to_purple(self, count: int = 1) -> int:
        converted = 0
        for _ in range(count):
            candidates = [(c, self.counts[c]) for c in BASE_COLORS if self.counts[c] > 0]
            if not candidates:
                break
            colors, weights = zip(*candidates)
            chosen = random.choices(colors, weights=weights, k=1)[0]
            self.counts[chosen] -= 1
            self.counts["purple"] += 1
            converted += 1
        return converted


@dataclass
class Card:
    name: str
    kind: str  # "cat" or "dog"
    cost: int
    effect: Dict[str, str]
    description: str


@dataclass
class Player:
    name: str
    is_ai: bool
    bag: Bag
    kibbles: float = 0.0
    total_score: float = 0.0
    cat_cards: List[Card] = field(default_factory=list)
    dog_cards: List[Card] = field(default_factory=list)
    stolen_dog_cards: List[Card] = field(default_factory=list)
    objective_color: Optional[str] = None
    extra_rerolls: int = 0
    pending_extra_rerolls: int = 0
    pending_roll_bonus: int = 0
    pending_nimble_dice: int = 0
    turn_nimble_dice: int = 0
    free_dog_claims: int = 0
    free_cat_claims: int = 0
    pending_roll_penalty: int = 0
    pending_roll_penalty_round: int = 0
    pending_reroll_block: bool = False
    pending_reroll_block_round: int = 0
    pending_grudge_bonus: int = 0
    rerolls_blocked: bool = False
    starlight_round: int = 0
    blocked_dog_card: Optional[Card] = None
    blocked_dog_round: int = 0
    blocked_dog_active: bool = False
    temp_dog_cards: List[Card] = field(default_factory=list)
    focus_overrides: Dict[int, str] = field(default_factory=dict)
    shadow_dawg_triggered_round: int = 0
    bull_dawg_triggered_round: int = 0


@dataclass
class ScoreResult:
    score: int
    name: str
    color_bonus: int
    dice: List[Die]
    all_same_color: bool
    extra_points: int = 0
    straight_high: int = 0
    value_overrides: Optional[Dict[int, int]] = None

    @property
    def total(self) -> int:
        return self.score + self.color_bonus + self.extra_points


@dataclass
class DogModifiers:
    color_die_bonus: Dict[str, int] = field(default_factory=dict)
    small_straight_as_large: bool = False
    large_straight_bonus: int = 0
    all_same_color_points: int = 0
    straight_bonus: int = 0
    four_kind_as_five: bool = False
    four_kind_bonus: int = 0
    straight_dup_bonus: int = 0
    full_house_bonus: int = 0
    solitary_color_bonus: int = 0
    all_same_color_kibbles: int = 0
    color_pair_bonus: int = 0
    pair_bonus: int = 0
    three_kind_bonus: int = 0
    no_score_bonus: int = 0
    five_kind_bonus: int = 0
    purple_die_bonus: int = 0
    mythic_bonus: int = 0
    objective_color: Optional[str] = None
    force_zero: bool = False


class Deck:
    def __init__(self, cards: List[Card], name: str = "deck") -> None:
        self._base = list(cards)
        self._cards: List[Card] = []
        self._name = name
        self._reshuffle()

    def _reshuffle(self, exclude: Optional[List[Card]] = None) -> None:
        if not exclude:
            self._cards = list(self._base)
        else:
            counts: Dict[Tuple[str, str], int] = {}
            for card in exclude:
                key = (card.name, card.kind)
                counts[key] = counts.get(key, 0) + 1
            filtered: List[Card] = []
            for card in self._base:
                key = (card.name, card.kind)
                if counts.get(key, 0) > 0:
                    counts[key] -= 1
                    continue
                filtered.append(card)
            self._cards = filtered
        random.shuffle(self._cards)
        self._log_counts()

    def _log_counts(self) -> None:
        counts: Dict[str, int] = {}
        for card in self._cards:
            counts[card.name] = counts.get(card.name, 0) + 1
        parts = [f"{name}:{count}" for name, count in sorted(counts.items())]
        total = len(self._cards)
        print(f"[Deck] {self._name} reshuffle -> {total} cards | " + ", ".join(parts))

    def draw(self, exclude: Optional[List[Card]] = None) -> Optional[Card]:
        if not self._cards:
            self._reshuffle(exclude=exclude)
            if not self._cards:
                return None
        return self._cards.pop()

    def reshuffle(self, exclude: Optional[List[Card]] = None) -> None:
        self._reshuffle(exclude=exclude)

    def add(self, card: Card) -> None:
        self._cards.append(card)
        random.shuffle(self._cards)


def _add_cards(
    cards: List[Card],
    name: str,
    kind: str,
    cost: int,
    description: str,
    count: int,
) -> None:
    for _ in range(count):
        cards.append(Card(name, kind, cost, {}, description))


def build_cat_cards() -> List[Card]:
    cards: List[Card] = []
    _add_cards(cards, "Cat Burglar", "cat", 2, "Take a dog card from another player.", 4)
    _add_cards(cards, "Regal Cat", "cat", 2, "Double current kibbles.", 4)
    _add_cards(cards, "Lap Cat", "cat", 2, "Gain +1 reroll on your next turn.", 4)
    _add_cards(
        cards,
        "Momma Cat",
        "cat",
        2,
        "Next turn, roll +2 dice (stackable twice, max 9).",
        4,
    )
    _add_cards(cards, "Feral Cat", "cat", 2, "Convert 1 die in your bag to purple wild.", 8)
    _add_cards(cards, "Nimble Cat", "cat", 2, "Reroll 2 dice without discarding them next turn.", 8)
    _add_cards(cards, "Devil Cat", "cat", 2, "Reroll 3 dice to 6 for free this turn.", 2)
    _add_cards(
        cards,
        "Starlight Cat",
        "cat",
        2,
        "Purple dice become wild values this round.",
        2,
    )
    _add_cards(cards, "Bat Cat", "cat", 2, "Discard 2 dice from your bag of your choice.", 8)
    _add_cards(cards, "Stray Cat", "cat", 2, "Draft 2 dice of any color from the dice bank.", 8)
    _add_cards(cards, "Fish Bone Cat", "cat", 2, "Add 1 purple die to your bag.", 2)
    _add_cards(
        cards,
        "Pummeling Puma",
        "cat",
        2,
        "Block all rerolls for an opponent next round (Momma Cat still works).",
        4,
    )
    _add_cards(cards, "Void Cat", "cat", 2, "Steal a cat card from another player.", 4)
    _add_cards(cards, "Lion Cut Cat", "cat", 2, "Move one of your dog cards to stolen dogs.", 2)
    _add_cards(cards, "Territorial Cat", "cat", 2, "Block one dog card next round.", 4)
    _add_cards(cards, "Present Cat", "cat", 2, "Earn 4 kibbles instantly.", 2)
    _add_cards(cards, "Tolerant Cat", "cat", 2, "Buy 1 dog card for free this shop.", 2)
    _add_cards(
        cards,
        "Dogs Best Friend",
        "cat",
        2,
        "Select a dog card to copy for this round (stacks).",
        2,
    )
    _add_cards(
        cards,
        "Cat Tackle",
        "cat",
        2,
        "Draft 2 dice for another player from the dice bank.",
        2,
    )
    _add_cards(
        cards,
        "Raccoon Cat",
        "cat",
        2,
        "Steal up to 2 kibbles from another player.",
        2,
    )
    _add_cards(
        cards,
        "Focus Cat",
        "cat",
        2,
        "Change one die to your objective color for this round.",
        4,
    )
    _add_cards(
        cards,
        "Narc Cat",
        "cat",
        2,
        "Remove 1 purple die from an opponent's bag (not usable in shop).",
        4,
    )
    _add_cards(
        cards,
        "Greedy Cat",
        "cat",
        2,
        "Target player rolls 1 fewer die next round (stacks).",
        4,
    )
    _add_cards(
        cards,
        "Squirrel Cat",
        "cat",
        2,
        "Add 4 random dice to another player's bag.",
        2,
    )
    _add_cards(
        cards,
        "Shrodinger's Cat",
        "cat",
        2,
        "Reroll your scoring hand and keep the higher scoring result.",
        2,
    )
    _add_cards(
        cards,
        "Thief in the Night",
        "cat",
        2,
        "Steal any cat or dog card from any player, and bank 3 kibbles.",
        2,
    )
    return cards


def build_dog_cards() -> List[Card]:
    cards: List[Card] = []
    _add_cards(cards, "Big Dawg Energy", "dog", 4, "Small runs score as large runs.", 2)
    _add_cards(cards, "Barrel Dawg", "dog", 4, "One pair gives +1 point.", 4)
    _add_cards(cards, "Tri-tail Dawg", "dog", 4, "Three of a kind gains +1 point.", 4)
    _add_cards(cards, "Service Dawg", "dog", 4, "Zero-score hand gains 8 points.", 4)
    _add_cards(cards, "Bull Dawg", "dog", 4, "If you reroll all dice, gain +1 reroll (once per round).", 2)
    _add_cards(cards, "Alpha Dawg", "dog", 4, "Dog cards cost 1 less kibble.", 2)
    _add_cards(cards, "Mascot Dawg", "dog", 4, "If you are not the round leader, gain +2 kibbles.", 2)
    _add_cards(cards, "Golden Dawg", "dog", 4, "Shop purchase limit +1.", 4)
    _add_cards(cards, "Scurvy Dawg", "dog", 4, "If you score 0, gain +2 kibbles.", 4)
    _add_cards(cards, "Shadow Dawg", "dog", 4, "If an opponent uses a cat card this round, gain +1 reroll next round.", 2)
    _add_cards(cards, "Cats Best Friend", "dog", 4, "Increase cat limit by +1.", 2)
    _add_cards(cards, "Psychedelic Dawg", "dog", 4, "Purple wild dice score +1 each.", 4)
    _add_cards(cards, "Reservoir Dawgs", "dog", 4, "Large runs score +1 point.", 2)
    _add_cards(cards, "Who Let the Dawgs Out?", "dog", 4, "All same color gains +2 points.", 2)
    _add_cards(cards, "4 Shot Saluki", "dog", 4, "Four of a kind scores as five. Each extra Saluki adds the base hand score again.", 2)
    _add_cards(cards, "Dawg House", "dog", 4, "Full house gains +1 point.", 2)
    _add_cards(cards, "One Dawg Wolf Pack", "dog", 4, "Each solitary color gains +1 point.", 2)
    _add_cards(cards, "Best Buddies", "dog", 4, "All same color gains +2 kibbles.", 2)
    _add_cards(cards, "Snuggle Buddies", "dog", 4, "Color pairs gain +2 points each.", 2)
    _add_cards(cards, "Diamond Dawg", "dog", 4, "Five of a kind gains +1 point.", 2)
    _add_cards(cards, "Goodest Dawg", "dog", 4, "If you finish 3rd or 4th, gain +2 kibbles.", 4)
    _add_cards(cards, "Street Dawg", "dog", 4, "If you are not the overall score leader, +5 points per copy.", 2)
    _add_cards(
        cards,
        "Pit Baws",
        "dog",
        4,
        "Force a zero-scoring hand while active (synergy: Service/Scurvy).",
        1,
    )
    _add_cards(
        cards,
        "Daredevil Dawg",
        "dog",
        4,
        "Double all +1 dog boosts; 1-in-4 chance to return to deck after round.",
        2,
    )
    _add_cards(
        cards,
        "Where's Rufus",
        "dog",
        4,
        "First roll each round includes at least 1 objective die per copy.",
        4,
    )
    _add_cards(
        cards,
        "Grudge Dawg",
        "dog",
        4,
        "Any time you are stolen from, gain +6 to your round score.",
        2,
    )
    _add_cards(
        cards,
        "Mythic Dawg",
        "dog",
        4,
        "If you score four of a kind or better, double the base hand score.",
        2,
    )
    return cards


def build_dog_modifiers(player: Player) -> DogModifiers:
    mods = DogModifiers()
    if player.objective_color in BASE_COLORS:
        mods.objective_color = player.objective_color
    daredevil_multiplier = 1
    if any(
        c.name == "Daredevil Dawg"
        for c in (player.dog_cards + player.stolen_dog_cards + player.temp_dog_cards)
    ):
        daredevil_multiplier = 2
    for card in player.dog_cards + player.stolen_dog_cards + player.temp_dog_cards:
        if player.blocked_dog_active and card is player.blocked_dog_card:
            continue
        if card.name == "Lake Dawg":
            mods.color_die_bonus["blue"] = mods.color_die_bonus.get("blue", 0) + 1
        elif card.name == "Grass Dawg":
            mods.color_die_bonus["green"] = mods.color_die_bonus.get("green", 0) + 1
        elif card.name == "Scaredy Dawg":
            mods.color_die_bonus["yellow"] = mods.color_die_bonus.get("yellow", 0) + 1
        elif card.name == "Fire Dawg":
            mods.color_die_bonus["red"] = mods.color_die_bonus.get("red", 0) + 1
        elif card.name == "Big Dawg Energy":
            mods.small_straight_as_large = True
            mods.straight_dup_bonus += 1
        elif card.name == "Psychedelic Dawg":
            mods.purple_die_bonus += 1 * daredevil_multiplier
        elif card.name == "Reservoir Dawgs":
            mods.large_straight_bonus += 1 * daredevil_multiplier
        elif card.name == "Who Let the Dawgs Out?":
            mods.all_same_color_points += 2
        elif card.name == "4 Shot Saluki":
            mods.four_kind_as_five = True
            mods.four_kind_bonus += 1
        elif card.name == "Dawg House":
            mods.full_house_bonus += 1 * daredevil_multiplier
        elif card.name == "One Dawg Wolf Pack":
            mods.solitary_color_bonus += 1 * daredevil_multiplier
        elif card.name == "Best Buddies":
            mods.all_same_color_kibbles += 2
        elif card.name == "Snuggle Buddies":
            mods.color_pair_bonus += 2
        elif card.name == "Diamond Dawg":
            mods.five_kind_bonus += 1 * daredevil_multiplier
        elif card.name in ("Barrel Dawg", "Barrel Dog"):
            mods.pair_bonus += 1 * daredevil_multiplier
        elif card.name == "Tri-tail Dawg":
            mods.three_kind_bonus += 1 * daredevil_multiplier
        elif card.name == "Service Dawg":
            mods.no_score_bonus += 1
        elif card.name == "Mythic Dawg":
            mods.mythic_bonus += 1
        elif card.name == "Pit Baws":
            mods.force_zero = True
    return mods


def _evaluate_score(
    values: List[int],
    colors: List[str],
    mods: DogModifiers,
    purple_count: int,
) -> Tuple[int, int, str, bool]:
    if mods.force_zero:
        return 0, 0, "No score", False
    counts: Dict[int, int] = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    count_list = sorted(counts.values(), reverse=True)

    unique_vals = sorted(set(values))
    is_large_straight = len(unique_vals) == 5 and max(unique_vals) - min(unique_vals) == 4
    is_small_straight = False
    if len(unique_vals) >= 4:
        for start in range(1, 4):
            needed = set(range(start, start + 4))
            if needed.issubset(unique_vals):
                is_small_straight = True
                break

    base_score = 0
    name = "No score"
    if 5 in count_list:
        base_score, name = 8, "Five of a kind"
    elif 4 in count_list:
        base_score, name = 6, "Four of a kind"
    elif is_large_straight:
        base_score, name = 5, "Large straight"
    elif count_list == [3, 2]:
        base_score, name = 3, "Full house"
    elif is_small_straight:
        base_score, name = 3, "Small straight"
    elif 3 in count_list:
        base_score, name = 2, "Three of a kind"
    elif count_list == [2, 2, 1] or (len(values) == 4 and count_list == [2, 2]):
        base_score, name = 2, "Two pair"
    elif 2 in count_list:
        base_score, name = 1, "Pair"

    if base_score == 0:
        return 0, 0, "No score", False

    if name == "Small straight" and mods.small_straight_as_large:
        base_score, name = 5, "Small straight (as large)"
    if name == "Four of a kind" and mods.four_kind_as_five:
        base_score, name = 8, "Four of a kind (as five)"
    hand_base = base_score
    if name == "Pair":
        base_score += mods.pair_bonus
    if name == "Three of a kind":
        base_score += mods.three_kind_bonus
    if name == "Full house":
        base_score += mods.full_house_bonus
    if name == "Five of a kind":
        base_score += mods.five_kind_bonus
        if mods.four_kind_bonus > 1:
            base_score += (mods.four_kind_bonus - 1) * 8
    if name == "Four of a kind" or name == "Four of a kind (as five)":
        if mods.four_kind_bonus > 1:
            base_score += (mods.four_kind_bonus - 1) * 6
    if "straight" in name and mods.straight_bonus > 1:
        base_score += mods.straight_bonus - 1
    if "straight" in name and mods.straight_dup_bonus > 1:
        large_for_bonus = ("Large straight" in name) or ("as large" in name)
        straight_base = 5 if large_for_bonus else 3
        base_score += straight_base * (mods.straight_dup_bonus - 1)
    if name == "Large straight":
        base_score += mods.large_straight_bonus
    if mods.mythic_bonus and ("Four of a kind" in name or "Five of a kind" in name):
        base_score += hand_base * mods.mythic_bonus

    color_counts: Dict[str, int] = {}
    for c in colors:
        color_counts[c] = color_counts.get(c, 0) + 1
    all_same_color = len(color_counts) == 1 and len(values) > 0

    color_bonus = 1 if all_same_color else 0
    if all_same_color:
        color_bonus += mods.all_same_color_points

    extra = 0
    if mods.objective_color:
        extra += sum(1 for c in colors if c == mods.objective_color)
    for c in colors:
        extra += mods.color_die_bonus.get(c, 0)
    extra += mods.purple_die_bonus * purple_count
    solitary = sum(1 for count in color_counts.values() if count == 1)
    extra += mods.solitary_color_bonus * solitary
    pairs = sum(1 for count in color_counts.values() if count == 2)
    extra += mods.color_pair_bonus * pairs

    extra_points = 0
    return base_score + extra, color_bonus, name, all_same_color


def score_five(dice: List[Die], mods: DogModifiers) -> ScoreResult:
    return score_five_with_overrides(dice, mods, None)


def score_five_with_overrides(
    dice: List[Die],
    mods: DogModifiers,
    color_overrides: Optional[Dict[int, str]] = None,
    value_wild_ids: Optional[set[int]] = None,
) -> ScoreResult:
    values = [d.value for d in dice]

    def effective_color(die: Die) -> str:
        if color_overrides and id(die) in color_overrides:
            return color_overrides[id(die)]
        return die.color

    colors = [effective_color(d) for d in dice]
    purple_indices = [i for i, color in enumerate(colors) if color == "purple"]
    purple_count = len(purple_indices)
    wild_value_indices = [
        i for i, die in enumerate(dice) if value_wild_ids and id(die) in value_wild_ids
    ]

    best = ScoreResult(0, "No score", 0, dice, False)
    best_straight_high = 0

    def straight_high(vals: List[int]) -> int:
        unique_vals = sorted(set(vals))
        if len(unique_vals) < 4:
            return 0
        if len(unique_vals) == 5 and max(unique_vals) - min(unique_vals) == 4:
            return max(unique_vals)
        highs = []
        for start in range(1, 4):
            needed = set(range(start, start + 4))
            if needed.issubset(unique_vals):
                highs.append(start + 3)
        return max(highs) if highs else 0

    if not purple_indices and not wild_value_indices:
        score, color_bonus, name, all_same = _evaluate_score(values, colors, mods, purple_count)
        extra_points = 0
        if name == "No score" and mods.no_score_bonus:
            extra_points = 8 * mods.no_score_bonus
        straight_score = straight_high(values)
        return ScoreResult(
            score,
            name,
            color_bonus,
            dice,
            all_same,
            extra_points,
            straight_score,
        )

    color_assignments = (
        [()] if not purple_indices else itertools.product(BASE_COLORS, repeat=len(purple_indices))
    )
    value_assignments = (
        [()] if not wild_value_indices else itertools.product(range(1, 7), repeat=len(wild_value_indices))
    )

    for assignment in color_assignments:
        if not purple_indices:
            trial_colors = list(colors)
        else:
            trial_colors = []
            assignment_iter = iter(assignment)
            for color in colors:
                if color == "purple":
                    trial_colors.append(next(assignment_iter))
                else:
                    trial_colors.append(color)
        for value_assignment in value_assignments:
            trial_values = list(values)
            current_overrides: Optional[Dict[int, int]] = None
            if wild_value_indices:
                current_overrides = {}
                for idx, val in zip(wild_value_indices, value_assignment):
                    trial_values[idx] = val
                    current_overrides[id(dice[idx])] = val
            score, color_bonus, name, all_same = _evaluate_score(
                trial_values, trial_colors, mods, purple_count
            )
            extra_points = 0
            if name == "No score" and mods.no_score_bonus:
                extra_points = 8 * mods.no_score_bonus
            current_total = score + color_bonus + extra_points
            current_straight_high = straight_high(trial_values)
            if (
                current_total > best.total
                or (current_total == best.total and current_straight_high > best_straight_high)
            ):
                best = ScoreResult(
                    score,
                    name,
                    color_bonus,
                    dice,
                    all_same,
                    extra_points,
                    current_straight_high,
                    current_overrides,
                )
                best_straight_high = current_straight_high
    return best


def best_score(
    all_dice: List[Die],
    player: Player,
    color_overrides: Optional[Dict[int, str]] = None,
    value_wild_ids: Optional[set[int]] = None,
) -> ScoreResult:
    mods = build_dog_modifiers(player)
    if len(all_dice) < 5:
        return score_five_with_overrides(all_dice, mods, color_overrides, value_wild_ids)
    best = ScoreResult(0, "No score", 0, [], False)
    best_straight_high = 0
    for indices in itertools.combinations(range(len(all_dice)), 5):
        subset = [all_dice[i] for i in indices]
        result = score_five_with_overrides(subset, mods, color_overrides, value_wild_ids)
        straight_high = result.straight_high
        if (
            result.total > best.total
            or (result.total == best.total and straight_high > best_straight_high)
        ):
            best = result
            best_straight_high = straight_high
    return best


class Game:
    def __init__(self, players: List[Player], max_cat_cards: int = 2, max_dog_cards: int = 5) -> None:
        self.players = players
        self.round_num = 1
        self.turn_index = 0
        self.current_hand: List[Die] = []
        self.set_aside: List[Die] = []
        self.rerolls_left = 0
        self.max_cat_cards = max(1, max_cat_cards)
        self.max_dog_cards = max(1, max_dog_cards)
        self.cat_deck = Deck(build_cat_cards(), name="cat")
        self.dog_deck = Deck(build_dog_cards(), name="dog")
        self.shop_cats: List[Card] = []
        self.shop_dogs: List[Card] = []

    def max_cat_limit(self, player: Player) -> int:
        bonus = sum(
            1
            for c in (player.dog_cards + player.stolen_dog_cards)
            if c.name == "Cats Best Friend"
        )
        return max(1, self.max_cat_cards + bonus)

    def dog_card_cost(self, player: Player, card: Card) -> int:
        if card.kind != "dog":
            return card.cost
        daredevil_multiplier = 1
        if any(
            c.name == "Daredevil Dawg"
            for c in (player.dog_cards + player.stolen_dog_cards + player.temp_dog_cards)
        ):
            daredevil_multiplier = 2
        alpha_bonus = sum(
            1
            for c in (player.dog_cards + player.stolen_dog_cards)
            if c.name == "Alpha Dawg"
        )
        return max(0, card.cost - (alpha_bonus * daredevil_multiplier))

    def start_turn(self, player: Player) -> None:
        self.current_hand = []
        self.set_aside = []
        self.rerolls_left = 2 + player.extra_rerolls + player.pending_extra_rerolls
        player.rerolls_blocked = False
        if player.focus_overrides:
            player.focus_overrides.clear()
        player.pending_extra_rerolls = 0
        roll_bonus = min(player.pending_roll_bonus, 4)
        player.pending_roll_bonus = 0
        roll_penalty = 0
        if player.pending_roll_penalty_round == self.round_num and player.pending_roll_penalty > 0:
            roll_penalty = player.pending_roll_penalty
            player.pending_roll_penalty = 0
            player.pending_roll_penalty_round = 0
        roll_count = min(9, 5 + roll_bonus - roll_penalty)
        roll_count = max(1, roll_count)
        player.turn_nimble_dice = player.pending_nimble_dice
        player.pending_nimble_dice = 0
        if player.pending_reroll_block_round == self.round_num and player.pending_reroll_block:
            self.rerolls_left = 0
            player.rerolls_blocked = True
            player.pending_reroll_block = False
            player.pending_reroll_block_round = 0
        colors = player.bag.draw(roll_count)
        if player.objective_color in BASE_COLORS and colors:
            rufus_count = sum(
                1
                for c in (player.dog_cards + player.stolen_dog_cards + player.temp_dog_cards)
                if c.name == "Where's Rufus"
            )
            if rufus_count > 0:
                required = min(roll_count, rufus_count)
                current = sum(1 for c in colors if c == player.objective_color)
                needed = max(0, required - current)
                if needed > 0:
                    available = player.bag.counts.get(player.objective_color, 0)
                    swap_indices = [i for i, c in enumerate(colors) if c != player.objective_color]
                    swaps = min(needed, available, len(swap_indices))
                    for _ in range(swaps):
                        swap_idx = random.choice(swap_indices)
                        swap_indices.remove(swap_idx)
                        player.bag.add(colors[swap_idx], 1)
                        player.bag.counts[player.objective_color] -= 1
                        colors[swap_idx] = player.objective_color
        for color in colors:
            self.current_hand.append(Die(color, random.randint(1, 6)))

    def reroll(self, player: Player, indices: List[int]) -> List[int]:
        if self.rerolls_left <= 0:
            return []
        if not indices:
            return []

        full_reroll = len(indices) >= len(self.current_hand) and len(self.current_hand) > 0
        has_bull = any(
            c.name == "Bull Dawg"
            for c in (player.dog_cards + player.stolen_dog_cards + player.temp_dog_cards)
        )
        bull_available = (
            full_reroll
            and has_bull
            and player.bull_dawg_triggered_round != self.round_num
        )
        indices = sorted(set(indices))
        nimble_count = min(player.turn_nimble_dice, len(indices))
        nimble_indices = set(indices[:nimble_count])
        rerolled_positions: List[int] = []
        for idx in nimble_indices:
            if idx < len(self.current_hand):
                die = self.current_hand[idx]
                self.current_hand[idx] = Die(die.color, random.randint(1, 6))
                rerolled_positions.append(idx)
        player.turn_nimble_dice -= nimble_count

        remaining_indices = set(i for i in indices if i not in nimble_indices)
        if remaining_indices:
            kept: List[Die] = []
            for idx, die in enumerate(self.current_hand):
                if idx in remaining_indices:
                    self.set_aside.append(die)
                else:
                    kept.append(die)
            self.current_hand = kept

            replacements = player.bag.draw(len(remaining_indices))
            for color in replacements:
                self.current_hand.append(Die(color, random.randint(1, 6)))
            rerolled_positions.extend(
                range(len(self.current_hand) - len(replacements), len(self.current_hand))
            )

        self.rerolls_left -= 1
        if bull_available:
            self.rerolls_left += 1
            player.bull_dawg_triggered_round = self.round_num
        return rerolled_positions

    def finish_turn(
        self,
        player: Player,
        color_overrides: Optional[Dict[int, str]] = None,
    ) -> ScoreResult:
        value_wild_ids = None
        if getattr(player, "starlight_round", 0) == self.round_num:
            wild_ids = {id(die) for die in self.current_hand if die.color == "purple"}
            if wild_ids:
                value_wild_ids = wild_ids
        result = best_score(self.current_hand, player, color_overrides, value_wild_ids)
        for die in self.current_hand + self.set_aside:
            player.bag.add(die.color, 1)
        self.current_hand = []
        self.set_aside = []
        self.rerolls_left = 0
        if player.focus_overrides:
            player.focus_overrides.clear()
        if player.blocked_dog_active:
            player.blocked_dog_active = False
            player.blocked_dog_card = None
            player.blocked_dog_round = 0
        return result

    def award_kibbles(self, scores: List[Tuple[Player, ScoreResult]]) -> None:
        sorted_scores = sorted(scores, key=lambda s: s[1].total, reverse=True)
        if not sorted_scores:
            return
        unique_scores = []
        for _, s in sorted_scores:
            if s.total not in unique_scores:
                unique_scores.append(s.total)
        payout_by_rank = {0: 4.0, 1: 3.0, 2: 2.0, 3: 2.0}
        for player, result in sorted_scores:
            rank = unique_scores.index(result.total)
            if rank in payout_by_rank:
                player.kibbles += payout_by_rank[rank]

        standings = [p for p, _ in sorted_scores]
        if standings:
            leader_kibbles = max(p.kibbles for p in standings)
        else:
            leader_kibbles = 0
        for player, result in sorted_scores:
            mods = build_dog_modifiers(player)
            if result.all_same_color and mods.all_same_color_kibbles > 0:
                player.kibbles += mods.all_same_color_kibbles
            goodest_count = sum(
                1
                for card in player.dog_cards + player.stolen_dog_cards + player.temp_dog_cards
                if card.name == "Goodest Dawg"
            )
            if goodest_count and player in standings[-2:]:
                player.kibbles += 2 * goodest_count
            mascot_count = sum(
                1
                for card in player.dog_cards + player.stolen_dog_cards + player.temp_dog_cards
                if card.name == "Mascot Dawg"
            )
            if mascot_count and result.total < unique_scores[0]:
                player.kibbles += 2 * mascot_count
            scurvy_count = sum(
                1
                for card in player.dog_cards + player.stolen_dog_cards + player.temp_dog_cards
                if card.name == "Scurvy Dawg"
            )
            if scurvy_count and result.total == 0:
                player.kibbles += 2 * scurvy_count

    def prepare_shop(self) -> None:
        self.shop_cats = []
        self.shop_dogs = []
        for _ in range(2):
            self.shop_cats.append(self.draw_cat())
        for _ in range(3):
            self.shop_dogs.append(self.draw_dog())

    def draw_cat(self) -> Optional[Card]:
        exclude = []
        for player in self.players:
            exclude.extend(player.cat_cards)
        exclude.extend([c for c in self.shop_cats if c])
        return self.cat_deck.draw(exclude=exclude)

    def draw_dog(self) -> Optional[Card]:
        exclude = []
        for player in self.players:
            exclude.extend(player.dog_cards)
            exclude.extend(player.stolen_dog_cards)
        exclude.extend([c for c in self.shop_dogs if c])
        return self.dog_deck.draw(exclude=exclude)

    def apply_card(self, player: Player, card: Card) -> None:
        if card.kind == "dog":
            return
        if card.name == "Cat Burglar":
            return
        elif card.name == "Regal Cat":
            before = player.kibbles
            player.kibbles *= 2
            gain = player.kibbles - before
            if gain > 6:
                player.kibbles = before + 6
        elif card.name == "Lap Cat":
            player.pending_extra_rerolls += 1
        elif card.name == "Momma Cat":
            player.pending_roll_bonus = min(player.pending_roll_bonus + 2, 4)
        elif card.name == "Nimble Cat":
            player.pending_nimble_dice += 2
        elif card.name == "Present Cat":
            player.kibbles += 4
        elif card.name == "Tolerant Cat":
            player.free_dog_claims += 1

    def use_cat_card(self, player: Player, card: Card) -> bool:
        if card not in player.cat_cards:
            return False
        player.cat_cards.remove(card)
        self.apply_card(player, card)
        return True

    def can_buy(self, player: Player, card: Card, replace_cat: bool = False, replace_dog: bool = False) -> bool:
        if card.kind == "cat" and len(player.cat_cards) >= self.max_cat_limit(player) and not replace_cat:
            return False
        if card.kind == "dog" and len(player.dog_cards) >= self.max_dog_cards and not replace_dog:
            return False
        if card.kind == "dog" and player.free_dog_claims > 0:
            return True
        if card.kind == "dog":
            return player.kibbles >= self.dog_card_cost(player, card)
        return player.kibbles >= card.cost

    def buy_card(
        self,
        player: Player,
        card: Card,
        replace_cat: Optional[Card] = None,
        replace_dog: Optional[Card] = None,
    ) -> bool:
        allow_replace = replace_cat is not None
        allow_dog_replace = replace_dog is not None
        if not self.can_buy(player, card, replace_cat=allow_replace, replace_dog=allow_dog_replace):
            return False
        free = card.kind == "dog" and player.free_dog_claims > 0
        if not free:
            cost = card.cost
            if card.kind == "dog":
                cost = self.dog_card_cost(player, card)
            player.kibbles -= cost
        else:
            player.free_dog_claims -= 1
        if card.kind == "cat":
            if replace_cat and replace_cat in player.cat_cards:
                player.cat_cards.remove(replace_cat)
            player.cat_cards.append(card)
        else:
            if replace_dog and replace_dog in player.dog_cards:
                player.dog_cards.remove(replace_dog)
            player.dog_cards.append(card)
        return True
