#!/usr/bin/env python3

import argparse
from functools import total_ordering
from hearthstone.cardxml import load_dbf
from hearthstone.deckstrings import Deck


@total_ordering
class Card:
    def __init__(self, data):
        self._data = data

    def __hash__(self):
        return self._data.dbf_id

    def __str__(self):
        return self._data.name

    def __eq__(self, other):
        return self._data.dbf_id == other._data.dbf_id

    def __lt__(self, other):
        return self._data.cost < other._data.cost


def load_cards():
    db = load_dbf()[0]
    cards = {}
    for dbf_id in db:
        cards[dbf_id] = Card(db[dbf_id])
    return cards


def load_deck(deckstring, cards):
    return frozenset(
        map(
            lambda x: (cards[x[0]], x[1]),
            Deck.from_deckstring(deckstring).cards,
        )
    )


def main():
    """
    Diff Hearthstone decks.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("deckstring1")
    parser.add_argument("deckstring2")
    args = parser.parse_args()

    cards = load_cards()
    deck1 = load_deck(args.deckstring1, cards)
    deck2 = load_deck(args.deckstring2, cards)
    for card, count in sorted(deck1 - deck2):
        print("- ", card, count)
    for card, count in sorted(deck2 - deck1):
        print("+ ", card, count)


if __name__ == "__main__":
    main()
