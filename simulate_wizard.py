"""
Holds the classes use to simulate Wizard
"""
import numpy as np
from dataclasses import dataclass
from collections import Counter


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
    def _create_new_deck():
        cards = []

        for suit in ['hearts', 'clubs', 'spades', 'diamonds']:
            for number in range(2, 15): # Aces are 15
                a_card = Card(number=number,suit=suit, special=None)
                cards.append(a_card)

        for special in ['wizard','jester']:
            for number in range(0,4):
                special_card = Card(number = number, suit=None, special=special)
                cards.append(special_card)
        np.random.shuffle(cards)
        return cards

    
    def deal_cards(self, N_cards:int) -> list:
        cards_dealt = [self.cards_in_deck.pop(-1) for _ in range(N_cards)]
        return cards_dealt



class Hand:
    """
    The cards a Player is holding
    """

    def __init__(self, cards):
        self.cards = cards
        self.suits = [card.suit for card in self.cards] # unclear if I can use the method


    def _compute_suits_in_hand(self):
        """
            Given the cards in self.cards, returns a list of suits that this player has
        """
        self.suits = set([card.suit for card in self.cards if card.suit is not None])


    def _get_valid_cards(self, suit_lead):
        """
        Given the suit lead returns a list of all the cards this player can play
        """
        if suit_lead is None:
            return self.cards

        cards_in_suit = [card for card in self.cards if card.suit is suit_lead]
        if len(cards_in_suit) == 0:
            np.random.shuffle(self.cards)
            return self.cards
        else:
            special_cards = [card for card in self.cards if card.special is not None]
            special_cards.extend(cards_in_suit)
            np.random.shuffle(special_cards)
            return special_cards


    def play_random_valid_card(self, suit_lead) -> Card:
        """
        Given the suit lead returns a random and playable card
        """
        valid_cards = self._get_valid_cards(suit_lead=suit_lead)
        
        random_valid_card = valid_cards[0]
        self.cards = [card for card in self.cards if card != random_valid_card]
        self._compute_suits_in_hand()
        return random_valid_card

    def __str__(self) -> str:
        return str([card.__str__() for card in self.cards])

    def __repr__(self) -> str:
        return self.__str__()
    


class Player:

    def __init__(self, hand:Hand, position):
        self.hand = hand
        self.position = position


    def play_random_valid_card(self, suit_lead):
        if len(self.hand.cards) > 0:
            return self.hand.play_random_valid_card(suit_lead)
        else:
            raise ValueError("You cannot play cards from a hand that does not have any.")


    def __str__(self) -> str:
        return f'Position_{self.position} cards:{self.hand.__str__()}'


    def __repr__(self) -> str:
        return self.__str__()



class Game:

    def __init__(self, n_players:int, n_cards:int):
        self.deck = Deck()
        self.n_players = n_players
        self.n_cards = n_cards
        self.players = [Player(Hand(self.deck.deal_cards(n_cards)), position=position) for position in range(n_players)]
        self.trump = Game._determine_trump_suit(self.deck)
        self.play_order = Game._create_play_order_dict(self.players)
    

    @staticmethod
    def _determine_trump_suit(deck):
        trump_card = deck.deal_cards(N_cards=1)[0]
        if trump_card.special == None:
            return trump_card.suit
        elif trump_card.special == 'wizard':
            return np.random.choice(['hearts', 'clubs', 'spades', 'diamonds'], size=1)[0]
        elif trump_card.special == 'jester':
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


    def compute_results(self) ->list:
        """
        """
        starting_hands = [(player.position,player.hand.cards) for player in self.players]
        first_staring_player = self.players[0]
        winners = []
        for _ in range(self.n_cards):
            a_trick = Trick(self.deck, players_in_order=self.play_order[first_staring_player])
            a_trick.get_winner_and_update_hands(self.trump)
            winners.append(a_trick.winner.position)

        winner_collections = Counter(winners)
        
        results = []
        for hand in starting_hands: 
            # this is broken, it is only recording a record for each hand. You need to do it for every starting hand
            cards_in_hand = hand[1]
            n_won = winner_collections[hand[0]]
            res = {
                'n_players':self.n_players,
                'n_cards':self.n_cards,
                'n_won':n_won,
                'trump':self.trump,
                'hand':cards_in_hand
                 }

            results.append(res)
        
        return results



class Trick:

    def __init__(self, deck:Deck, players_in_order:list): 
        
        self.players_in_order = players_in_order
        self.winner= None


    def get_players_to_play_trick(self):
        """
        returns a list of tuples of (Player, card_played, position_played_at)
        """       
        first_player =  self.players_in_order[0]
        first_played_card = first_player.play_random_valid_card(suit_lead=None)
        if first_played_card.special == 'wizard':
            suit_lead = None
        elif first_played_card.special == 'jester':
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





import pandas as pd


def tester():
    deck = Deck()
    n_players = 7
    n_cards = 3
    a_game = Game(n_players=n_players, n_cards=n_cards)

    res = a_game.compute_results()
    df = pd.DataFrame.from_records(res)
    print(df.head(5))

if __name__ =="__main__":
    tester()