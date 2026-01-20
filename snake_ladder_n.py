#!/usr/bin/env python3
"""
Snake & Ladder (CLI) — N×N Board (Interactive)
----------------------------------------------
- Asks for board size N and player names at start (with sensible defaults).
- Still supports command-line flags; prompts let you override or accept defaults.

Usage examples:
  python3 snake_ladder_nxn.py                 # prompts for N and player names
  python3 snake_ladder_nxn.py --size 12       # default N=12 in prompt (you can override there)
  python3 snake_ladder_nxn.py --players "You,Alice,Computer 1"
  python3 snake_ladder_nxn.py --overshoot bounce --cascade --seed 42
"""
from __future__ import annotations
import argparse
import random
from typing import Dict, List, Tuple, Set

DEFAULT_LADDERS_10x10 = {
    2: 38, 7: 14, 8: 31, 15: 26, 21: 42,
    28: 84, 36: 44, 51: 67, 71: 91, 78: 98
}
DEFAULT_SNAKES_10x10 = {
    16: 6, 46: 25, 49: 11, 62: 19, 64: 60,
    74: 53, 89: 68, 92: 88, 95: 75, 99: 80
}

class Player:
    def __init__(self, name: str) -> None:
        self.name = name
        self.pos = 0

    @property
    def is_bot(self) -> bool:
        return self.name.lower().startswith('computer')

    def __repr__(self) -> str:
        return f"Player(name={self.name!r}, pos={self.pos})"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Snake & Ladder CLI on an N×N board (interactive)")
    p.add_argument('--size', type=int, default=10, help='Board dimension N (board is N×N). Default 10')
    p.add_argument('--players', type=str, default='You,Computer 1',
                   help='Comma-separated player names. Names starting with "Computer" are bots.')
    p.add_argument('--snakes', type=int, default=None, help='Number of snakes to auto-generate')
    p.add_argument('--ladders', type=int, default=None, help='Number of ladders to auto-generate')
    p.add_argument('--seed', type=int, default=None, help='Random seed for reproducibility')
    p.add_argument('--dice-sides', type=int, default=6, help='Dice faces (default 6)')
    p.add_argument('--overshoot', choices=['stay', 'bounce'], default='stay',
                   help="Overshoot behavior: 'stay' (default) or 'bounce' back from the end")
    p.add_argument('--cascade', action='store_true', help='Apply snakes/ladders repeatedly (chain effects)')
    return p.parse_args()


def roll_dice(sides: int = 6) -> int:
    return random.randint(1, sides)


def generate_snakes_ladders(target: int, n: int, snakes: int, ladders: int,
                             avoid: Set[int] = None) -> Tuple[Dict[int, int], Dict[int, int]]:
    avoid = set(avoid or [])
    avoid.update({1, target})

    S: Dict[int, int] = {}
    L: Dict[int, int] = {}
    used_starts: Set[int] = set()
    used_ends: Set[int] = set()

    def add_pair(is_ladder: bool) -> bool:
        tries = 0
        while tries < 5000:
            tries += 1
            start = random.randint(2, target - 1)
            if start in avoid or start in used_starts:
                continue
            if is_ladder:
                end = random.randint(start + 1, target - 1)
            else:
                end = random.randint(2, start - 1)
            if end in avoid or end in used_ends:
                continue
            if abs(end - start) < max(2, n // 2):
                continue
            if is_ladder:
                if end in used_starts or end in used_ends:
                    continue
                if end in S.keys():
                    continue
                L[start] = end
                used_starts.add(start)
                used_ends.add(end)
                return True
            else:
                if end in used_starts or end in used_ends:
                    continue
                if start in L.values():
                    continue
                S[start] = end
                used_starts.add(start)
                used_ends.add(end)
                return True
        return False

    ladder_quota = ladders
    snake_quota = snakes
    toggle = True
    while ladder_quota > 0 or snake_quota > 0:
        if toggle and ladder_quota > 0:
            if add_pair(is_ladder=True):
                ladder_quota -= 1
            else:
                break
        elif (not toggle) and snake_quota > 0:
            if add_pair(is_ladder=False):
                snake_quota -= 1
            else:
                break
        toggle = not toggle

    return S, L


def apply_snake_ladder(pos: int, snakes: Dict[int, int], ladders: Dict[int, int], cascade: bool=False) -> int:
    if not cascade:
        if pos in ladders:
            print(f"  🎉 Ladder! {pos} → {ladders[pos]}")
            return ladders[pos]
        if pos in snakes:
            print(f"  🐍 Snake! {pos} → {snakes[pos]}")
            return snakes[pos]
        return pos
    current = pos
    while True:
        moved = False
        if current in ladders:
            nxt = ladders[current]
            print(f"  🎉 Ladder! {current} → {nxt}")
            current = nxt
            moved = True
        elif current in snakes:
            nxt = snakes[current]
            print(f"  🐍 Snake! {current} → {nxt}")
            current = nxt
            moved = True
        if not moved:
            return current


def overshoot_move(curr: int, roll: int, target: int, mode: str) -> int:
    tentative = curr + roll
    if tentative == target:
        return target
    if tentative < target:
        return tentative
    if mode == 'stay':
        print(f"  Needs exact roll to reach {target}. Stay at {curr}.")
        return curr
    over = tentative - target
    bounced = target - over
    print(f"  Overshoot! Bounce from {target} to {bounced}.")
    return bounced


def turn_step(player, target, dice_sides, snakes, ladders, overshoot_mode, cascade):
    if not player.is_bot:
        input(f"\n{player.name}, press Enter to roll the dice… ")
    d = roll_dice(dice_sides)
    print(f"  🎲 {player.name} rolled a {d}.")
    tentative = overshoot_move(player.pos, d, target, overshoot_mode)
    new_pos = apply_snake_ladder(tentative, snakes, ladders, cascade=cascade)
    player.pos = new_pos
    print(f"  {player.name} moves to {player.pos}.")
    if player.pos == target:
        print(f"\n🏁 {player.name} wins! 🏆")
        return True
    return False


def prompt_int(prompt: str, default: int, min_value: int = 1) -> int:
    while True:
        s = input(f"{prompt} [default {default}]: ").strip()
        if not s:
            return default
        try:
            val = int(s)
            if val < min_value:
                print(f"  Please enter an integer ≥ {min_value}.")
                continue
            return val
        except ValueError:
            print("  Please enter a valid integer.")


def prompt_players(default_csv: str) -> List[str]:
    while True:
        s = input(f"Enter player names (comma-separated) [default {default_csv}]: ").strip()
        csv = s if s else default_csv
        names = [n.strip() for n in csv.split(',') if n.strip()]
        if len(names) < 2:
            print("  Please enter at least two players.")
            continue
        return names


def main():
    args = parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    # Interactive prompts to ASK for N and player names
    print("\n=== Snake & Ladder — Interactive Setup ===")
    N = prompt_int("Enter board size N (N×N board, N ≥ 2)", default=max(2, args.size), min_value=2)
    names = prompt_players(args.players)

    target = N * N
    players = [Player(n) for n in names]

    # Snakes & Ladders setup
    if N == 10 and args.snakes is None and args.ladders is None:
        snakes = dict(DEFAULT_SNAKES_10x10)
        ladders = dict(DEFAULT_LADDERS_10x10)
    else:
        snakes_count = args.snakes if args.snakes is not None else max(5, N)
        ladders_count = args.ladders if args.ladders is not None else max(5, N)
        avoid = {2, 3, target-1, target-2}
        snakes, ladders = generate_snakes_ladders(target, N, snakes_count, ladders_count, avoid=avoid)

    # Banner
    print("\n=== Snake & Ladder (CLI) — N×N Board ===")
    print(f"Board size: {N}×{N}  |  Target: {target}  |  Dice: d{args.dice_sides}")
    print(f"Overshoot: {args.overshoot}  |  Cascade: {'on' if args.cascade else 'off'}")
    print("Players:", ", ".join(p.name for p in players))

    # Show snakes and ladders
    if snakes:
        print("\nSnakes:")
        for h, t in sorted(snakes.items()):
            print(f"  {h} → {t}")
    else:
        print("\nSnakes: (none)")
    if ladders:
        print("Ladders:")
        for s, e in sorted(ladders.items()):
            print(f"  {s} → {e}")
    else:
        print("Ladders: (none)")

    print("\nRules: exact roll required to finish (or bounce if enabled). Good luck!\n")

    # Game loop
    winner = None
    while not winner:
        for p in players:
            if turn_step(p, target, args.dice_sides, snakes, ladders, args.overshoot, args.cascade):
                winner = p
                break

if __name__ == '__main__':
    main()