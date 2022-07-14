"""
Holds the parts of the game
"""

from collections import Counter
from dataclasses import dataclass

import numpy as np

HEARTS = 'hearts'
CLUBS = 'clubs'
SPADES = 'spades'
DIAMONDS = 'diamonds'

WIZARD = 'wizard'
JESTER = 'jester'

SUITS = [HEARTS, CLUBS, SPADES, DIAMONDS]
SPECIALS = [WIZARD, JESTER]

@dataclass(eq=True, frozen=True, order=True)
class Card:
    number: int
    suit: str
    special: str = None

    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self):
        if self.special is None:
            return f'{self.number}-{self.suit}'
        return f'{self.special}'


class Deck:
    def __init__(self):
        self.cards_in_deck = Deck._create_new_deck()

    @staticmethod
    def _create_new_deck(include_special=True) -> set[Card]:
        cards = set([Card(number, suit, None) for suit in SUITS for number in range(2, 15)])
        if include_special:
            special_cards = [Card(0, None, special) for special in SPECIALS for _ in range(4)]
            cards.extend(special_cards)
        return cards
    
    def deal_cards(self, N_cards:int) -> list[Card]:
        """
        Returns a list of N cards dealt from the top of the deck
        """
        return [self.cards_in_deck.pop() for _ in range(N_cards)]


class Hand:
    """
    The cards a Player is holding. the cards
    """
    def __init__(self, cards: set[Card]):
        self.starting_cards = cards.copy()
        self.cards = cards
        self.cards_by_suit: dict[str, set(Card)] = self._build_cards_by_suit()

    def _build_cards_by_suit(self):
        """Re update the cards by suit in cards"""
        d = dict()
        for suit in SUITS:
            d[suit] = set()
        for card in self.cards:
            d[card.suit].add(card)
        return d

    def _get_playable_cards(self, suit_lead: str) -> set[Card]:
        """
        Given the suit lead returns a set of all the cards that it is legal for the player to play
        """
        if suit_lead is None:
            return self.cards # if no suit lead then you can play any card
        playable_cards = self.cards_by_suit[suit_lead]
        if len(playable_cards) > 0:
            playable_cards.update(self.cards_by_suit[None]) # add the special cards since you can always play them
        else:
            playable_cards = self.cards
        return playable_cards

    def attempt_to_play_card(self, suit_lead: str, card: Card):
        valid_cards = self._get_playable_cards(suit_lead=suit_lead)
        if card in valid_cards and card in self.cards:
            self.cards.discard(card)
            return card
        else:
            raise ValueError(f'cannot play card {card} because it is not valid or not in hand {self}')

    def play_random_valid_card(self, suit_lead) -> Card:
        """
        Given the suit lead returns a random and playable card
        """
        valid_cards = self._get_playable_cards(suit_lead=suit_lead)
        random_valid_card = valid_cards.pop()
        return self.attempt_to_play_card(suit_lead, random_valid_card)

    def __str__(self) -> str:
        return str([str(card) for card in self.cards])

    def __repr__(self) -> str:
        return self.__str__()
    




class Game:

    def __init__(self, n_players:int, n_cards:int):
        self.deck = Deck()
        self.n_players = n_players
        self.n_cards = n_cards
        self.players = [Player(Hand(self.deck.deal_cards(n_cards)), position) for position in range(n_players)]
        self.trump = Game._determine_trump_suit(self.deck)
        self.play_order = Game._create_play_order_dict(self.players)
    

    @staticmethod
    def _determine_trump_suit(deck):
        trump_card = deck.deal_cards(1)[0]
        if trump_card.special == None:
            return trump_card.suit
        elif trump_card.special == WIZARD:
            return np.random.choice(SUITS, size=1)[0]
        elif trump_card.special == JESTER:
            return None

    @staticmethod
    def _create_play_order_dict(players) -> dict:
        """
        creates a dictionary of (starting_player: Player +1, Player +2 player +3 for each player in players)

        Used to decide the order of play
        """
        players.sort(key=lambda player: player.position) # sort by postion 0 at start N at end
        play_order = dict()
        for starting_player in players:
            players_greater_position = [player for player in players if player.position >= starting_player.position]
            players_lesser_postion  = [player for player in players if player.position < starting_player.position ]
            players_greater_position.extend(players_lesser_postion)
            play_order[starting_player] = players_greater_position
        
        return play_order


    # def compute_results(self) ->list:
    #     """
    #     """
    #     starting_hands = [(player.position, player.hand.cards) for player in self.players] # (positon, cards in hand tuple)
    #     first_staring_player = self.players[0]
    #     winners = []
    #     for _ in range(self.n_cards):
    #         a_trick = Trick(self.deck, players_in_order=self.play_order[first_staring_player])
    #         a_trick.get_winner_and_update_hands(self.trump)
    #         winners.append(a_trick.winner.position)

    #     winner_collections = Counter(winners)
        
    #     results = []
    #     for hand in starting_hands: 
    #         # this is broken, it is only recording a record for each hand. You need to do it for every starting hand
    #         cards_in_hand = hand[1]
    #         n_won = winner_collections[hand[0]]
    #         res = {
    #             'n_players':self.n_players,
    #             'n_cards':self.n_cards,
    #             'n_won':n_won,
    #             'trump':self.trump,
    #             'hand':cards_in_hand
    #              }

    #         results.append(res)
        
    #     return results



class Trick:
    """A Single hand of cards"""

    def __init__(self, players_in_order: list[Player]): 
        self.players_in_order = players_in_order
        self.winner = None

    def get_players_to_play_trick(self):
        """
        returns a list of tuples of (Player, card_played, position_played_at)
        """       
        first_player =  self.players_in_order[0]
        first_played_card = first_player.play_random_valid_card(suit_lead=None)
        if first_played_card.special == WIZARD:
            suit_lead = None
        elif first_played_card.special == JESTER:
            suit_lead = None 
            # solve this later it add inaccuarcy to a hand
            # but it ought not to matter at this scale
        else:
            suit_lead = first_played_card.suit


        who_played_what_when_tuple = (first_player, first_played_card, 0)
        cards_played_in_order = [who_played_what_when_tuple]

        for i, player in enumerate(self.players_in_order[1:]):
            next_random_valid_card =  player.play_random_valid_card(suit_lead=suit_lead)
            who_played_what_when_tuple = (player, next_random_valid_card, i+1)
            cards_played_in_order.append(who_played_what_when_tuple)

        return cards_played_in_order


    def compute_who_won_trick(self, cards_played_in_order, trump):

        current_winning_player = cards_played_in_order[0][0]
        current_winning_card = cards_played_in_order[0][1]

        if trump != None:
            for next_player, next_card, index in cards_played_in_order[1:]:
                if (current_winning_card.special == 'wizard') or (next_card.special == 'jester'):
                    break
                elif (current_winning_card.special != 'wizard') and (next_card.special == 'wizard'):
                    current_winning_player = next_player
                    current_winning_card = next_card
                elif (current_winning_card.suit != trump) and (next_card.suit == trump):
                    # if the new card is trump and the old one is not then that card is trump
                    current_winning_player = next_player
                    current_winning_card = next_card
                elif current_winning_card.suit == next_card.suit:
                    # if the suits are the same then the larger number wins
                    if current_winning_card.number < next_card.number:
                        current_winning_player = next_player
                        current_winning_card = next_card


        else:
            suit_lead = current_winning_card.suit
            for next_player, next_card, index in cards_played_in_order[1:]:
                if (current_winning_card.special == 'wizard') or (next_card.special == 'jester'):
                    break
                elif (current_winning_card.special != 'wizard') and (next_card.special == 'wizard'):
                    current_winning_player = next_player
                    current_winning_card = next_card
                elif (current_winning_card.special!='wizard') and (next_card.special == 'wizard'):
                    current_winning_player = next_player
                    current_winning_card = next_card
                    
                elif next_card.suit == suit_lead:
                    # if the suits are the same then the larger number wins
                    if current_winning_card.number < next_card.number:
                        current_winning_player = next_player
                        current_winning_card = next_card


        return current_winning_player


    def get_winner_and_update_hands(self, trump):
        cards_played_in_order = self.get_players_to_play_trick()
        winning_player = self.compute_who_won_trick(cards_played_in_order=cards_played_in_order,trump=trump)
        self.winner = winning_player
