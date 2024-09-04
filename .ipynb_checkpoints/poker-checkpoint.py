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
    To give an example, if we imagine we have an Ace-high flush, we will report our hand as (5, 14), indicating flush, 
    ace high. The second number will represent the strength of the second strongest card. In the case of the 1 paired hands, this
    is the same as the strength of the strongest card. We do this all the way down through the strength of the hand. 
    The reason to do this is to determine who wins in the case of tie breaks.
    
    This function will largely be written as a series of if statements, I suppose. I'm not sure how else to think through the 
    complexity of the hand. 
    """
    rank_counter = defaultdict(int)
    suit_counter = defaultdict(int)
    for card in hand:
        rank_counter[card.rank] += 1
        suit_counter[card.suit] += 1

    ## check for straight flush (or just flush)
    
    for key in suit_counter.keys():
        if suit_counter[key] >= 5:
            suit_of_interest = key
            cards_of_suit = []
            for card in hand:
                if card.suit == suit_of_interest:
                    cards_of_suit.append(card)
        
            ranks = [card.rank for card in cards_of_suit]
            sorted(ranks)
            ranks = set(ranks)
            for i in range(13, 3, -1):
                straight_order = np.arange(i-4, i+1)
                if len(ranks.intersection(straight_order)) == 5:
                    return (8, straight_order[-1], straight_order[-2], straight_order[-3], straight_order[-4], straight_order[-5])
            ace_low_sf = [13, 0, 1, 2, 3]
            if len(ranks.intersection(ace_low_sf)) == 5:
                return(8, 3, 2, 1, 0, 13)
                
    ## check for 4 of a kind
    for key in rank_counter.keys():
        if rank_counter[key] == 4:
            rank_of_interest = key
            ranks = []
            for key in rank_counter.keys():
                if key != rank_of_interest:
                    ranks.append(key)
            sorted(ranks)
            return (7, rank_of_interest, rank_of_interest, rank_of_interest, rank_of_interest, ranks[-1])
            
    ## check for full houses
    ranks = reversed(sorted(list(rank_counter.keys()))) ## sort by ranks from highest to lowest
    for key in ranks:
        if rank_counter[key] == 3:
            for other_key in ranks:
                if other_key != key and rank_counter[other_key] >= 2:
                    return (6, key, key, key, other_key, other_key)

    ## check for flush
    for key in suit_counter.keys():
        if suit_counter[key] >= 5:
            suit_of_interest = key
            ranks = []
            for card in hand:
                if card.suit == suit_of_interest:
                    ranks.append(card.rank)
            sorted(ranks)
            ranks = ranks[-5:] ## take highest five card flush. no need to check for straight flush as we have done this already.
            return (5, ranks[-1], ranks[-2], ranks[-3], ranks[-4], ranks[-5]) 

    ## check for straight
    ranks = set(sorted(list(rank_counter.keys())))
    if len(ranks) >= 5:
        for i in range(13, 3, -1):
            straight = np.arange(i-4, i+1)
            if len(ranks.intersection(straight)) == 5:
                return (4, straight[-1], straight[-2], straight[-3], straight[-4], straight[-5])
        ace_low_straight = set([13, 0, 1, 2, 3])
        if len(ranks.intersection(ace_low_straight)) == 5:
            return (4, 3, 2, 1, 0, 13)
            
    ## check for 3 of a kind
    reversed(sorted(list(rank_counter.keys())))
    for rank in ranks:
        if rank_counter[rank] == 3:
            for other_rank in ranks:
                if other_rank != rank:
                    kicker_1 = other_rank
            for other_rank in ranks:
                if other_rank != rank and other_rank != kicker_2:
                    kicker_2 = other_rank
            return (3, rank, rank, rank, kicker_1, kicker_2)

    ## check for 2 pair
    for rank in ranks:
        if rank_counter[rank] == 2:
            for other_rank in ranks:
                if other_rank != rank and rank_counter[other_rank] == 2:
                    for kicker in ranks:
                        if kicker != rank and kicker != other_rank:
                            return (2, rank, rank, other_rank, other_rank, kicker)

    ## check for 1 pair
    for rank in ranks:
        if rank_counter[rank] == 2:
            for other_rank in ranks:
                if other_rank != rank:
                    kicker_1 = other_rank
            for other_rank in ranks:
                if other_rank != rank and other_rank != kicker_1:
                    kicker_2 = other_rank
            for other_rank in ranks:
                if other_rank != rank and other_rank != kicker_1 and other_rank != kicker_2:
                    kicker_3 = other_rank
            return (1, rank, rank, kicker_1, kicker_2, kicker_3)

    ## Return high card hand
    return (0, ranks[0], ranks[1], ranks[2], ranks[3], ranks[4])