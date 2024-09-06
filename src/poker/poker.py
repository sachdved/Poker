import numpy as np
import scipy as sp

import random

from collections import defaultdict


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


class CommunityCards():
    """
    A class to represent the available community cards. This class
    does nothing but stores the cards.
    """
    def __init__(
        self,
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


def hand_strength(
    hand: list
):
    """
    Takes in a 7-card hand and returns the hand strength of the best possible five-card hand from
    the 7-card hand, and its strength. Hand strength is returned as a 6-tuple, where the first number is as follows:
    0: high card
    1: 1 pair
    2: 2 pair
    3: three of a kind
    4: straight
    5: flush
    6: full house
    7: four of a kind
    8: straight flush

    In order to deal with ties, the second number will represent the strength of the 'strongest' card in the hand. 
    To give an example, if we imagine we have an Ace-high flush, we will report our hand as (5, 13), indicating flush, 
    ace high. The second number will represent the strength of the second strongest card. In the case of the 1 paired hands, this
    is the same as the strength of the strongest card. We do this all the way down through the strength of the hand. 
    The reason to do this is to determine who wins in the case of tie breaks.

    In the case of straights, they can be ace low or ace high. Ace high straights would be denoted (4, 13, 12, 11, 10, 9)
    and ace low straights would be denoted (4, 3, 2, 1, 0, 13).
    
    This function will largely be written as a series of if statements, I suppose. I'm not sure how else to think through the 
    complexity of the hand. 
    """
    rank_counter = defaultdict(int)
    suit_counter = defaultdict(int)
    for card in hand:
        rank_counter[card.rank] += 1
        suit_counter[card.suit] += 1

    ## check for straight flush
    flush, flush_ranks = _is_flush(hand)
    flush_ranks = sorted(flush_ranks)
    if flush:
        straight, straight_ranks = _is_straight(flush_ranks)
        if straight:
            return (8, straight_ranks[0], straight_ranks[1], straight_ranks[2], straight_ranks[3], straight_ranks[4])
                
    ## check for 4 of a kind
    quad_rank = [r for r in rank_counter.keys() if rank_counter[r] == 4]
    if len(quad_rank) != 0:
        kicker = sorted([r for r in rank_counter.keys() if rank_counter[r] != 4])
        return (7, quad_rank[0], quad_rank[0], quad_rank[0], quad_rank[0], kicker[-1])

    ## check for full houses
    trips_rank = [r for r in rank_counter.keys() if rank_counter[r] == 3] 
    doubles_rank = [r for r in rank_counter.keys() if rank_counter[r] >= 2]

    if len(trips_rank) != 0 and len(doubles_rank) != 0:
        trip_rank = max(trips_rank)
        doubles_rank_trip_removed = [k for k in doubles_rank if k != trip_rank]
        if len(doubles_rank_trip_removed) > 0:
            double_rank = max(doubles_rank_trip_removed)
            return (6, trip_rank, trip_rank, trip_rank, double_rank, double_rank)
    
    ## check for flush but not straight
    if flush and not straight:
        return (5, flush_ranks[-1], flush_ranks[-2], flush_ranks[-3], flush_ranks[-4], flush_ranks[-5])

    ## check for straight but not flush
    ranks = list(set(list(rank_counter.keys())))
    sorted_ranks = sorted(ranks)
    straight, straight_ranks = _is_straight(sorted_ranks)
    if straight:
        return (4, straight_ranks[0], straight_ranks[1], straight_ranks[2], straight_ranks[3], straight_ranks[4])
            
    ## check for 3 of a kind
    if len(trips_rank)==1:
        kickers = sorted([k for k in rank_counter.keys() if rank_counter[k] == 1])
        trip_rank = trips_rank[0]
        return (3, trip_rank, trip_rank, trip_rank, kickers[-1], kickers[-2])

    ## check for 2 pair
    if len(doubles_rank) >= 2:
        doubles_rank = sorted(doubles_rank)
        pair_1 = doubles_rank[-1]
        pair_2 = doubles_rank[-2]
        kicker = max([k for k in rank_counter.keys() if k != pair_1 and k != pair_2])
        return (2, pair_1, pair_1, pair_2, pair_2, kicker)

    ## check for 1 pair
    if len(doubles_rank) == 1:
        pair = doubles_rank[0]
        kickers = sorted([k for k in rank_counter.keys() if k != pair])
        return (1, pair, pair, kickers[-1], kickers[-2], kickers[-3])

    ## Return high card hand
    ranks = sorted(list(rank_counter.keys()))
    return (0, ranks[-1], ranks[-2], ranks[-3], ranks[-4], ranks[-5])

def _is_flush(hand):
    """
    Checks if the hand is a flush. This is written
    to reduce some of the code duplication in the hand
    strength computation. 

    Returns whether it is a flush or not, and the cards
    belong to the suit creating the flush.
    """
    suit_counter = defaultdict(int)
    for card in hand:
        suit_counter[card.suit] += 1
    for key in suit_counter.keys():
        if suit_counter[key] >= 5:
            ranks = [card.rank for card in hand if card.suit == key]
            return True, ranks
    return False, []

def _is_straight(sorted_ranks):
    """
    Checks if the hand is a straight, given the ranks in sorted order.

    Returns the highest possible straight, given the ranks, if possible.
    """
    sorted_ranks = list(reversed(sorted_ranks))
    for i in range(len(sorted_ranks)-4):
        if sorted_ranks[i] - sorted_ranks[i+4] == 4:
            return True, (sorted_ranks[i:i+5])

    if sorted_ranks[0] == 13:
        if sorted_ranks[-4:] == [3, 2, 1, 0]:
            return True, [3, 2, 1, 0, 13]
    return False, []
