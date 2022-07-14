from lib2to3.pytree import Base
from game_parts import Hand
from bidder import BaseBidder

class Player:

    def __init__(self, hand: Hand, position: int, bidder: BaseBidder):
        self.hand = hand # dynamic hands in the table
        self.position = position # the seat number at the table
        self.bidder = bidder 
        
        self.tricks_won: int = 0 # a counter of how many tricks this player has won

    def play_random_valid_card(self, suit_lead: str):
        if len(self.hand.cards) > 0:
            return self.hand.play_random_valid_card(suit_lead)
        else:
            raise ValueError("You cannot play cards from a hand that does not have any.")

    def __str__(self) -> str:
        return f'Position_{self.position} cards:{self.hand.__str__()}'

    def __repr__(self) -> str:
        return self.__str__()
