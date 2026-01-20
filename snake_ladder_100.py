#!/usr/bin/env python3
"""
Snake & Ladder (CLI)
--------------------
A classic two-to-four player text-based Snake & Ladder game.
Default: 2 players (You vs Computer). Supports exact roll to finish.

Run: python3 snake_ladder.py
"""
from __future__ import annotations
import random
from typing import Dict, List

# Standard board configuration (popular variant)
LADDERS: Dict[int, int] = {
    2: 40, 7: 14, 8: 31, 15: 26, 21: 42,
    28: 84, 36: 44, 51: 67, 71: 91, 78: 98
}
SNAKES: Dict[int, int] = {
    16: 6, 46: 25, 49: 11, 62: 19, 64: 60,
    74: 53, 89: 68, 92: 88, 95: 75, 99: 80
}
TARGET = 100

class Player:
    def __init__(self, name: str) -> None:
        self.name = name
        self.pos = 0

    def __repr__(self) -> str:  # For debugging
        return f"Player(name={self.name!r}, pos={self.pos})"


def roll_dice() -> int:
    return random.randint(1, 6)


def apply_snakes_ladders(position: int) -> int:
    # If landing on a ladder bottom, climb; if on snake head, slide down
    if position in LADDERS:
        print(f"  🎉 Ladder! Climb from {position} to {LADDERS[position]}.")
        return LADDERS[position]
    if position in SNAKES:
        print(f"  🐍 Snake! Slide from {position} to {SNAKES[position]}.")
        return SNAKES[position]
    return position


def turn_step(player: Player) -> bool:
    input(f"\n{player.name}, Press Enter to roll the dice… ")
    dice = roll_dice()
    print(f"  🎲 {player.name} rolled a {dice}.")

    tentative = player.pos + dice
    if tentative > TARGET:
        print(f"  Needs exact roll to reach 100. Stay at {player.pos}.")
        return False

    player.pos = apply_snakes_ladders(tentative)
    print(f"  {player.name} moves to {player.pos}.")

    if player.pos == TARGET:
        print(f"\n🏁 {player.name} Wins! 🏆")
        return True
    return False


def setup_players() -> List[Player]:
    print("\nWelcome to Snake & Ladder (CLI)!\n")
    try:
        n = input("How many players? (2-4) [default 2]: ").strip()
        n = int(n) if n else 2
        if n < 2 or n > 4:
            raise ValueError
    except ValueError:
        n = 2
        print("Using default of 2 players.")

    players: List[Player] = []
    for i in range(n):
        if i == 0:
            name = input("Enter Player 1 name [You]: ").strip() or "You"
        else:
            name = input(f"Enter Player {i+1} name [Computer {i}]: ").strip() or f"Computer {i}"
        players.append(Player(name))

    print("\nSnakes:")
    for head, tail in sorted(SNAKES.items()):
        print(f"  {head} → {tail}")
    print("Ladders:")
    for start, end in sorted(LADDERS.items()):
        print(f"  {start} → {end}")

    print("\nRules: exact roll required to land on 100.")
    return players


def main():
    players = setup_players()
    winner = None
    while not winner:
        for p in players:
            if turn_step(p):
                winner = p
                break

if __name__ == "__main__":
    main()
