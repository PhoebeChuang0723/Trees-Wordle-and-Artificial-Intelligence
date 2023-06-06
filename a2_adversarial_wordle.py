"""CSC111 Winter 2023 Assignment 2: Trees, Wordle, and Artificial Intelligence

Module Description
==================

This module contains a collection of Python classes and functions that you'll use on
this assignment to represent games of Adversarial Wordle. You are responsible for reading the
*docstrings* of this file to understand how to use these classes and functions, but should not
modify anything in this file except:

1. Uncommenting the @check_contracts decorators (see note above the AdversarialWordle class).
2. Modifying the run_example function and main block.

This file will not be submitted, and we will supply our own copy for testing purposes.

Note: as is standard for CSC111, we use a leading underscore to indicate private
functions, methods, and instance attributes. You don't have to worry about any of these,
and in fact shouldn't use them in this assignment!

Disclaimer: we didn't have time to make this file fully PythonTA-compliant.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2023 Mario Badr, David Liu, and Angela Zavaleta Bernuy.
"""
from __future__ import annotations
import copy
import random
from typing import Iterable, Optional

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from python_ta.contracts import check_contracts


# === NOTE ABOUT USING check_contracts (PLEASE READ!) ===
# Because this assignment involves longer computations, we recommend commenting out @check_contracts
# on the line below when running your code on the larger word sets. Doing so will speed up the running
# time of the AdversarialWordle methods. However, when first testing your code on smaller examples
# (which you should definitely do!), we recommend keeping @check_contracts uncommented to take
# advantage of the representation invariants and preconditions we've provided you. 😊
# @check_contracts
class AdversarialWordle:
    """A class representing the state of a game of Adversarial Wordle.

    Instance Attributes:
    - word_set: a set of the allowed words for this game
    - max_guesses: the maximum number of guesses the Guesser player is allowed to make in this game
    - word_size: the length of the words in this game
    - guesses: a list of the guesses made by the Guesser player
    - statuses: a list of the statuses returned by the Adversary player
                NOTE: unlike CSC110 Assignment 2, each status is represented as a tuple
                instead of a list.

    Representation Invariants:
    - len(self.word_set) > 0
    - self.word_size >= 1
    - self.max_guesses >= 1
    - len(self.guesses) in {len(self.statuses), len(self.statuses) + 1}
    - all(len(word) == self.word_size for word in self.word_set)
    - all(len(guess) == self.word_size for guess in self.guesses)
    - all(len(status) == self.word_size for status in self.statuses)
    - all(_is_valid_status(status) for status in self.statuses)
    """
    word_set: frozenset[str]  # frozenset is like set, but immutable
    word_size: int
    max_guesses: int
    guesses: list[str]
    statuses: list[tuple[str, ...]]  # tuple[str, ...] means "a tuple of strings"
    _possible_answers: frozenset[str]

    def __init__(self, word_set: Iterable[str], max_guesses: int) -> None:
        """Initialize a new Adversarial Wordle game with the given word_set and max_guesses.

        Preconditions:
        - len(word_set) > 0
        - all words in word_set have the same length
        - max_guesses >= 1
        """
        if isinstance(word_set, frozenset):
            self.word_set = word_set
        else:
            self.word_set = frozenset(word_set)
        self.word_size = len(next(iter(word_set)))
        self.max_guesses = max_guesses
        self.guesses = []
        self.statuses = []
        self._possible_answers = self.word_set

    def is_guesser_turn(self) -> bool:
        """Return whether it is the Guesser player's turn.
        """
        return len(self.guesses) == len(self.statuses)

    def record_guesser_move(self, guess: str) -> None:
        """Record the given guess made by the Guesser player.

        Preconditions:
        - self.is_guesser_turn()
        - len(guess) == self.word_size
        - guess in self._possible_answers
        """
        self.guesses.append(guess)

    def record_adversary_move(self, status: tuple[str, ...]) -> None:
        """Record the given status returned by the Adversary player.

        Preconditions:
        - not self.is_guesser_turn()
        - len(status) == self.word_size
        - _is_valid_status(status)
        """
        self.statuses.append(status)

        # Update self._possible_answers
        self._possible_answers = _find_correct_answers(self._possible_answers, self.guesses, self.statuses)

    def copy_and_record_guesser_move(self, guess: str) -> AdversarialWordle:
        """Return a copy of this game state with the given guess recorded.

        Preconditions:
        - self.is_guesser_turn()
        - len(guess) == self.word_size
        - guess in self._possible_answers
        """
        new_game = self._copy()
        new_game.record_guesser_move(guess)
        return new_game

    def copy_and_record_adversary_move(self, status: tuple[str, ...]) -> AdversarialWordle:
        """Return a copy of this game state with the given status recorded.

        Preconditions:
        - not self.is_guesser_turn()
        - len(status) == self.word_size
        - _is_valid_status(status)
        """
        new_game = self._copy()
        new_game.record_adversary_move(status)
        return new_game

    def _copy(self) -> AdversarialWordle:
        """Return a copy of this game state."""
        new_game = AdversarialWordle(self.word_set, self.max_guesses)
        new_game.word_size = self.word_size
        new_game.guesses.extend(self.guesses)
        new_game.statuses.extend(self.statuses)
        new_game._possible_answers = self._possible_answers
        return new_game

    def get_possible_answers(self) -> list[str]:
        """Return the possible answers for the current game state, or [] if a player has won the game.

        The words returned are consistent with the guesses and statuses that
        have been recorded. If len(self.guesses) == len(self.statuses) + 1,
        the last guess is ignored, since it does not yet have a corresponding status.
        """
        if self.get_winner() is None:
            return list(self._possible_answers)
        else:
            return []

    def get_status_for_answer(self, answer: str) -> tuple[str, ...]:
        """Return the status for the most recent guess with respect to the given answer.

        Preconditions:
        - not self.is_guesser_turn()
        """
        return _get_guess_status(answer, self.guesses[-1])

    def get_winner(self) -> Optional[str]:
        """Return the winner of the game ('Guesser' or 'Adversary').

        Return None if the game is not over.
        """
        if len(self.guesses) != len(self.statuses):
            # It is the Adversary's turn; no one has won yet
            return None
        elif len(self.statuses) == 0:
            # No moves have been made; no one has won yet
            return None
        elif all(s == CORRECT for s in self.statuses[-1]):
            # The Adversary returned an "all correct" guess; Guesser has won
            return 'Guesser'
        elif len(self.statuses) == self.max_guesses:
            # The Guesser has no more guesses; Adversary has won
            return 'Adversary'
        else:
            # It is the Guesser's turn; no one has won yet
            return None

    def get_move_sequence(self) -> list[str | tuple[str, ...]]:
        """Return the move sequence made in this game.

        The returned list alternates between guesses (str) and statuses (tuple[str, ...]):

            [self.guesses[0], self.statuses[0], self.guesses[1], self.statuses[1], ...]
        """
        moves_so_far = []
        for i in range(0, len(self.guesses)):
            moves_so_far.append(self.guesses[i])
            if i < len(self.statuses):  # self.statuses may be 1 shorter than self.guesses
                moves_so_far.append(self.statuses[i])

        return moves_so_far


################################################################################
# Guesser player classes
################################################################################
class Guesser:
    """An abstract class representing a Guesser player in Adversarial Wordle.

    This class can be subclassed to implement different strategies for the Guesser player.
    """
    def make_move(self, game: AdversarialWordle) -> str:
        """Return a guess given the current game.

        Preconditions:
        - game.is_guesser_turn()
        """
        raise NotImplementedError


class RandomGuesser(Guesser):
    """A Guesser player that always picks a random word that is consistent with past
    guesses and statuses.
    """

    def make_move(self, game: AdversarialWordle) -> str:
        """Return a guess given the current game.

        Randomly choose among all possible correct answers for the given game.

        Preconditions:
        - game.is_guesser_turn()
        """
        possible_answers = game.get_possible_answers()
        return random.choice(list(possible_answers))


################################################################################
# Adversary player classes
################################################################################
class Adversary:
    """An abstract class representing an Adversary player in Adversarial Wordle.

    This class can be subclassed to implement different strategies for the Adversary player.
    """
    def make_move(self, game: AdversarialWordle) -> tuple[str, ...]:
        """Return a status given the current game.

        Preconditions:
        - not game.is_guesser_turn()
        """
        raise NotImplementedError


class RandomAdversary(Adversary):
    """An Adversary player that always picks a random answer consistent with the previous rounds.

    Avoids picking the most recent guess whenever possible.
    """

    def make_move(self, game: AdversarialWordle) -> tuple[str, ...]:
        """Return a status given the current game.

        Randomly choose among all possible correct answers for the given game,
        EXCEPT the most recent guess (if possible---see below), and then return
        the status for the current guess with respect to that answer.

        If the most recent guess is the only possible correct answer, then
        the "all CORRECT" status is returned. But if there is at least one correct
        answer other than the most recent guess, then the guess is never selected.
        In other words, RandomAdversary avoids returning "all CORRECT" whenever possible.

        Preconditions:
        - not game.is_guesser_turn()
        """
        possible_answers = game.get_possible_answers()
        current_guess = game.guesses[-1]

        # Remove the current guess from the possible answers
        if len(possible_answers) > 1:
            possible_answers.remove(current_guess)

        # Select a random answer and return the corresponding status
        answer = random.choice(possible_answers)
        return game.get_status_for_answer(answer)


################################################################################
# Functions for running games
################################################################################
def run_game(guesser: Guesser, adversary: Adversary, word_set_file: str, max_guesses: int) -> AdversarialWordle:
    """Run an Adversarial Wordle game between the two given players.

    Use the words in word_set_file, and use max_guesses as the maximum number of guesses.

    Return the AdversarialWordle instance after the game is complete.

    Preconditions:
    - word_set_file is a non-empty with one word per line
    - all words in word_set_file have the same length
    - max_guesses >= 1
    """
    with open(word_set_file) as f:
        word_set = {str.strip(line.lower()) for line in f}

    game = AdversarialWordle(word_set, max_guesses)

    while game.get_winner() is None:
        guess = guesser.make_move(game)
        game.record_guesser_move(guess)
        status = adversary.make_move(game)
        game.record_adversary_move(status)

    return game


def run_games(num_games: int,
              guesser: Guesser, adversary: Adversary,
              word_set_file: str, max_guesses: int,
              print_game: bool = True,
              show_stats: bool = False) -> dict[str, int]:
    """Run num_games games of Adversary Wordle between the two given players.

    Use the given word_set_file and max_guesses (these parameters are the same as
    in run_game).

    Optional arguments:
    - print_game: print a record of each game (default: True)
    - show_stats: use Plotly to display statistics for the game runs (default: False)

    Preconditions:
        - num_games >= 1
        - same preconditions for word_set_file and max_guesses as run_game
    """
    stats = {'Guesser': 0, 'Adversary': 0}
    results = []
    for i in range(0, num_games):
        guesser_copy = copy.copy(guesser)
        adversary_copy = copy.copy(adversary)

        game = run_game(guesser_copy, adversary_copy, word_set_file, max_guesses)
        winner = game.get_winner()
        stats[winner] += 1
        results.append(winner)

        if print_game:
            print(f'Game {i} winner: {winner}. Moves: {game.get_move_sequence()}')

    for outcome in stats:
        print(f'{outcome}: {stats[outcome]}/{num_games} ({100.0 * stats[outcome] / num_games:.2f}%)')

    if show_stats:
        plot_game_statistics(results)

    return stats


def plot_game_statistics(results: list[str]) -> None:
    """Plot the outcomes and win probabilities for a given list of Adversarial Wordle game results.

    Preconditions:
        - all(r in {'Guesser', 'Adversary'} for r in results)
    """
    outcomes = [1 if result == 'Guesser' else 0 for result in results]

    cumulative_win_percentage = [sum(outcomes[0:i]) / i for i in range(1, len(outcomes) + 1)]
    rolling_win_percentage = \
        [sum(outcomes[max(i - 50, 0):i]) / min(50, i) for i in range(1, len(outcomes) + 1)]

    fig = make_subplots(rows=2, cols=1)
    fig.add_trace(go.Scatter(y=outcomes, mode='markers',
                             name='Outcome (1 = Guesser win, 0 = Adversary win)'),
                  row=1, col=1)
    fig.add_trace(go.Scatter(y=cumulative_win_percentage, mode='lines',
                             name='Guesser win percentage (cumulative)'),
                  row=2, col=1)
    fig.add_trace(go.Scatter(y=rolling_win_percentage, mode='lines',
                             name='Guesser win percentage (most recent 50 games)'),
                  row=2, col=1)
    fig.update_yaxes(range=[0.0, 1.0], row=2, col=1)

    fig.update_layout(title='Adversary Wordle Game Results', xaxis_title='Game')
    fig.show()


###################################################################################################
# Additional helper functions for Wordle rules (similar to CSC110 A2)
# You do NOT need to access any of the functions in this section to complete this assignment.
###################################################################################################
CORRECT = 'Y'
WRONG_POSITION = '?'
INCORRECT = 'N'

ALL_STATUSES = {CORRECT, WRONG_POSITION, INCORRECT}


def _is_wrong_position_char(answer: str, guess: str, i: int) -> bool:
    """Return whether the character status of guess[i] with respect to answer is WRONG_POSITION.

    Preconditions:
    - len(answer) == len(guess)
    - 0 <= i < len(answer)
    """
    return (
        guess[i] != answer[i] and
        any(j != i and guess[i] == answer[j] and guess[j] != answer[j]
            for j in range(0, len(answer)))
    )


def _get_character_status(answer: str, guess: str, i: int) -> str:
    """Return the character status of guess[i] with respect to answer.

    The return value is one of the three values {INCORRECT, WRONG_POSITION, CORRECT}.

    Preconditions:
    - len(answer) == len(guess)
    - 0 <= i < len(answer)
    """
    if answer[i] == guess[i]:
        return CORRECT
    elif _is_wrong_position_char(answer, guess, i):
        return WRONG_POSITION
    else:
        return INCORRECT


def _get_guess_status(answer: str, guess: str) -> tuple[str, ...]:
    """Return the guess status of the given guess with respect to answer.

    The return value is a list with the same length as guess, whose
    elements are all in the set {INCORRECT, WRONG_POSITION, CORRECT}.

    Preconditions:
    - answer != ''
    - len(answer) == len(guess)
    """
    return tuple(_get_character_status(answer, guess, i) for i in range(0, len(guess)))


def _is_correct_multiple(word: str, guesses: list[str], statuses: list[tuple[str, ...]]) -> bool:
    """Return whether the given word is a correct answer for the given guesses and statuses.

    If guesses and statuses have different lengths, ignore the leftover entries in the longer list.

    Preconditions:
    - all(len(word) == len(guess) for guess in guesses)
    - all(len(word) == len(status) for status in statuses)
    - all(_is_valid_status(status) for status in statuses)
    - word != ''
    """
    return all(_get_guess_status(word, guess) == status
               for guess, status in zip(guesses, statuses))


def _find_correct_answers(word_set: Iterable[str],
                          guesses: list[str], statuses: list[tuple[str, ...]]) -> frozenset[str]:
    """Return the words (from word_set) that are correct answer for the given guesses and statuses.

    If guesses and statuses have different lengths, ignore the leftover entries in the longer list.

    Preconditions:
    - all words in word_set have the same non-zero length
    - all(len(guesses[i]) == len(statuses[i]) for i in range(0, len(guesses)))
    - all(_is_valid_status(status) for status in statuses)
    """
    return frozenset(word for word in word_set if _is_correct_multiple(word, guesses, statuses))


def _is_valid_status(status: Iterable[str]) -> bool:
    """Return whether s is a valid status.

    A valid status is a list that contains only the three statuses in ALL_STATUSES.
    """
    return all(char_status in ALL_STATUSES for char_status in status)


###############################################################################
# Main block
###############################################################################
def run_example() -> None:
    """Run one or more example games using the official Wordle word set.
    """
    # Example with a single game
    # game = run_game(
    #     guesser=RandomGuesser(),
    #     adversary=RandomAdversary(),
    #     word_set_file='data/words/official_wordle.txt',
    #     max_guesses=3
    # )
    # print(game.get_winner())
    # print(game.get_move_sequence())

    run_games(
        num_games=100,
        guesser=RandomGuesser(),
        adversary=RandomAdversary(),
        word_set_file='data/words/official_wordle.txt',
        max_guesses=4,
        print_game=True,
        show_stats=True  # Try changing to True!
    )


if __name__ == '__main__':
    run_example()
