"""

Holds the logic to determine how much to bid on a game

"""

from abc import ABC, abstractmethod

import numpy as np

from game_parts import Hand, Card

def BaseBidder(ABC):
    """
    Base abstract class that handles the bidding logic
    """
    def __init__(self):
        pass

    @abstractmethod
    def compute_bid(self, hand: Hand, starting_position: int , n_players: int , n_cards: int, trump: str | None):
        pass


def RandomBidder(BaseBidder):
    """
    Bids randomly between (0, n_cards)
    """
    def compute_bid(self, hand: Hand, starting_position: int , n_players: int , n_cards: int, trump: str | None):
        return np.random.randint(0, n_cards)


def ConstantBidder(BaseBidder):
    """
    Always bids a constant value
    """
    def __init__(self, constant: int):
        self.constant = constant

    def compute_bid(self, hand: Hand, starting_position: int , n_players: int , n_cards: int, trump: str | None):
        return self.constant


def AverageBidder(BaseBidder):
    """
    Bids the the bid if they expect to make what the % of cards they would given the n_players and n_cards

    eg if 10 cards and 3 players -> int(10/3) -> 3
    """
    def compute_bid(self, hand: Hand, starting_position: int , n_players: int , n_cards: int, trump: str | None):
        return round(n_cards /  n_players)

