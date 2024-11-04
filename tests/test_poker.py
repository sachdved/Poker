import pytest
import poker
import numpy as np

def test_hand_strength():
    hand_straight_low = [
        poker.Card(suit=0, rank = 0),
        poker.Card(suit=1, rank = 1),
        poker.Card(suit=3, rank = 2),
        poker.Card(suit=2, rank = 3),
        poker.Card(suit=0, rank = 12),
    ]
    hand_strength_straight_low = poker.hand_strength(hand_straight_low)

    hand_straight_high = [
        poker.Card(suit=0, rank = 8),
        poker.Card(suit=1, rank = 12),
        poker.Card(suit=3, rank = 10),
        poker.Card(suit=2, rank = 9),
        poker.Card(suit=0, rank = 11),
    ]

    hand_strength_straight_high = poker.hand_strength(hand_straight_high)

    hand_flush = [
        poker.Card(suit=2, rank = 8),
        poker.Card(suit=2, rank = 12),
        poker.Card(suit=2, rank = 7),
        poker.Card(suit=2, rank = 9),
        poker.Card(suit=2, rank = 11),
    ]
    hand_strength_flush = poker.hand_strength(hand_flush)

    hand_two_pair = [
        poker.Card(suit=2, rank = 8),
        poker.Card(suit=3, rank = 8),
        poker.Card(suit=1, rank = 12),
        poker.Card(suit=2, rank = 12),
        poker.Card(suit=0, rank = 11),
    ]
    hand_strength_two_pair = poker.hand_strength(hand_two_pair)

    assert hand_strength_straight_high == (4, 12, 11, 10, 9, 8)
    assert hand_strength_straight_low == (4, 3, 2, 1, 0, 12)
    assert hand_strength_flush == (5, 12, 11, 9, 8, 7)
    assert hand_strength_two_pair == (2, 12, 12, 8, 8, 11)


def test_simulate_outcomes():
    hand = [
        poker.Card(suit=0, rank = 0),
        poker.Card(suit=1, rank = 0)
    ]

    hand_outcomes = poker.simulate_outcomes(hand)

    assert (np.round(hand_outcomes[:, 0], 2) == np.asarray(
        [0., 0.36, 0.4, 0.12, 0.01, 0.02, 0.09, 0.01, 0.]
    )).all()


def test_opposing_outcomes():
    hand = [
        poker.Card(suit=0, rank = 3),
        poker.Card(suit=1, rank = 3)
    ]

    outcomes = [(1, 7), (1, 0), (3, 3), (2, 6), (2, 2)]

    community = poker.CommunityCards()
    community.cards = [poker.Card(suit = suit, rank = rank) for (suit, rank) in outcomes]

    hand_outcomes = poker.simulate_opposing_outcomes(hand, community)

    assert (np.round(hand_outcomes[:, 0], 2) == np.asarray(
        [0.40, 0.47, 0.07, 0.01, 0.05, 0., 0., 0., 0.]
    )).all()
