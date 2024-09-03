import numpy as np
import scipy as sp

import random

class Card():
    """
    A class for playing cards. Each card is described by its suit and its rank.
    """
    def __init__(
        self,
        suit: int,
        rank: int
    ):
        """
        Identify the suit and rank of each card.
        """
        self.suit = suit
        self.rank = rank

def CommunityCards():
    """
    A class to represent the available community cards. This class
    does nothing but stores the cards.
    """
    def __init__(
        self,
        cards
    ):
        self.cards = []

class Deck():
    """
    A class for creating a deck using the Card class, with a given number of ranks and suits. 
    """
    def __init__(
        self,
        num_suits: int,
        num_ranks: int
    ):
        """
        Identify the number of suits and the number of ranks in the deck
        """
        self.num_suits = num_suits
        self.num_ranks = num_ranks

        self.create_deck()

    def create_deck(
        self
    ) -> None:
        self.deck = [Card(suit, rank) for suit in range(self.num_suits) for rank in range(self.num_ranks)]
        random.shuffle(self.deck)

    def deal_hole_cards(
        self,
        players: list,
        num_cards: int
    ) ->  None:
        """
        Deal a number of cards to each player's private hand
        """
        num_players = len(players)
        if num_players * num_cards > len(self.deck):
            raise Exception("Not enough cards in deck")
        for player in players:
            for i in range(num_cards):
                player.hole_cards.append(self.deck.pop(0))

    def deal_flop(
        self,
        community_cards: CommunityCards
    ) -> None:
        """
        Deal three cards to the community.
        """
        for i in range(3):
            community_cards.cards.append(self.deck.pop(0))

    def deal_turn(
        self,
        community_cards: CommunityCards
    ) -> None:
        """
        Deal one card (the turn) to the community.
        """
        community_cards.cards.append(self.deck.pop(0))

    def deal_river(
        self,
        community_cards: CommunityCards
    ) -> None:
        """
        Deal river card to the community.
        """
        community_cards.cards.append(self.deck.pop(0))

class Player():
    """
    A player at a poker table. They are characterized by
    stack size and number of chips that they have. They
    are capable of betting.
    """
    def __init__(
        self,
        chips: float,
        policy_model
    ):
        """
        Initialize with some number of chips and a policy model
        for making bets.
        """
        self.chips = chips
        self.policy_model = policy_model
        self.hole_cards = []

    def make_bet(
        self,
        previous_bet: float,
        minimum_allowable_raise: float,
        community_cards: CommunityCards
    ):
        """
        This needs some work. Would need to assess what the inputs to the policy model should be.
        Probably things like the other players, their stack sizes, etc...
        
        """
        return self.policy_model(previous_bet, minimum_allowable_raise, self.hole_cards, community_cards.cards)