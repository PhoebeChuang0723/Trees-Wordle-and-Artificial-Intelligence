"""CSC111 Winter 2023 Assignment 2: Trees, Wordle, and Artificial Intelligence (Part 1)

Instructions (READ THIS FIRST!)
===============================

This Python module contains the start of functions and/or classes you'll define
for Part 1 of this assignment. Please note that in addition to this file, you will
also need to modify a2_game_tree.py by following the instructions on the assignment
handout. You should NOT make any changes to a2_adversarial_wordle.py.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2023 Mario Badr, David Liu, and Isaac Waller.
"""
import csv
import random
from typing import Optional

import a2_game_tree
import a2_adversarial_wordle as aw  # aw is a short-form to save some typing


################################################################################
# Part 1, Question 2 (Loading Adversarial Wordle game datasets)
################################################################################
def load_game_tree(games_file: str) -> a2_game_tree.GameTree:
    """Return a new game tree based on games_file.

    Preconditions:
        - games_file refers to a csv file in the format described on the assignment handout

    Implementation hints:
        - You can review Tutorial 4 for how we read CSV files in Python.
        - You can call tuple(s) to convert a string s into a tuple of characters.
        - You can *ignore* type errors that PyCharm might display if you're mixing str
          and tuple[str, ...] in a list.
        - We strongly recommend testing this function with the smaller "single_moves.csv"
          and "small_sample.csv" before jumping to "guesser_wins.csv".
          (All of these files are located under data/games.)

    >>> tree1 = load_game_tree('data/games/small_sample.csv')
    >>> print(tree1)
    * -> Guesser's move
      sepal -> Adversary's move
      tiger -> Adversary's move
      hello -> Adversary's move
      reach -> Adversary's move
        ('?', 'N', 'Y', 'N', 'N') -> Guesser's move
          brawl -> Adversary's move
          quart -> Adversary's move
      allow -> Adversary's move
      music -> Adversary's move

    >>> tree2 = load_game_tree('data/games/single_moves.csv')
    >>> print(tree2)
    * -> Guesser's move
      sepal -> Adversary's move
      tiger -> Adversary's move
      hello -> Adversary's move
      reach -> Adversary's move
      allow -> Adversary's move
      music -> Adversary's move
    """
    GAME_START_MOVE = '*'
    game_tree = a2_game_tree.GameTree(GAME_START_MOVE)

    with open(games_file) as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            new_format_row = []
            for item in row:
                if '?' in item or 'N' in item or 'Y' in item:
                    new_format_row.append(tuple(item))
                else:
                    new_format_row.append(item)

            game_tree.insert_move_sequence(new_format_row)

    return game_tree


###############################################################################
# Part 1, Question 3 and 4 (Tree-based Random AIs)
###############################################################################
class RandomTreeGuesser(aw.Guesser):
    """An Adversarial Wordle Guesser that plays randomly based on a given GameTree.

    This player uses a game tree to make moves, descending into the tree as the game is played.
    On its turn:

        1. First it updates its game tree to its subtree corresponding to the move made by
           its opponent. If no subtree is found, its game tree is set to None.
        2. Then, if its game tree is not None, it picks its next move randomly from among
           the subtrees of its game tree, and then reassigns its game tree to that subtree.
           But if its game tree is None or has no subtrees, the player behaves like aw.RandomGuesser,
           and then sets its game tree to None.
    """
    # Private Instance Attributes:
    #   - _game_tree:
    #       The GameTree that this player uses to make its moves. If None, then this
    #       player behaves like aw.RandomGuesser.
    _game_tree: Optional[a2_game_tree.GameTree]

    def __init__(self, game_tree: Optional[a2_game_tree.GameTree]) -> None:
        """Initialize this player.

        Preconditions:
            - game_tree.move == a2_game_tree.GAME_START_MOVE
        """
        self._game_tree = game_tree

    def make_move(self, game: aw.AdversarialWordle) -> str:
        """Return a guess given the current game.

        Preconditions:
        - game.is_guesser_turn()
        """
        if self._game_tree is not None and self._game_tree.move != a2_game_tree.GAME_START_MOVE:
            if self._game_tree.get_subtrees() == []:
                self._game_tree = None
            else:
                self._game_tree = self._game_tree.find_subtree_by_move(game.get_move_sequence().pop())

        if self._game_tree is None or self._game_tree.get_subtrees() == []:
            possible_answers = game.get_possible_answers()
            return random.choice(list(possible_answers))

        else:
            self._game_tree = random.choice(list(self._game_tree.get_subtrees()))
            return self._game_tree.move


class RandomTreeAdversary(aw.Adversary):
    """An Adversarial Wordle Adversary that plays randomly based on a given GameTree.

    This uses the analogous strategy as RandomTreeGuesser, except its moves are statuses rather than guesses.
    """
    # Private Instance Attributes:
    #   - _game_tree:
    #       The GameTree that this player uses to make its moves. If None, then this
    #       player behaves like aw.RandomAdversary.
    _game_tree: Optional[a2_game_tree.GameTree]

    def __init__(self, game_tree: Optional[a2_game_tree.GameTree]) -> None:
        """Initialize this player.

        Preconditions:
            - game_tree.move == a2_game_tree.GAME_START_MOVE
        """
        self._game_tree = game_tree

    def make_move(self, game: aw.AdversarialWordle) -> tuple[str, ...]:
        """Return a status given the current game.

        Preconditions:
        - not game.is_guesser_turn()
        """
        if self._game_tree is not None:
            if self._game_tree.get_subtrees() == []:
                self._game_tree = None
            else:
                self._game_tree = self._game_tree.find_subtree_by_move(game.get_move_sequence().pop())

        if self._game_tree is None or self._game_tree.get_subtrees() == []:
            possible_answers = game.get_possible_answers()
            current_guess = game.guesses[-1]

            if len(possible_answers) > 1:
                possible_answers.remove(current_guess)

            answer = random.choice(possible_answers)
            return game.get_status_for_answer(answer)

        else:
            self._game_tree = random.choice(list(self._game_tree.get_subtrees()))
            return self._game_tree.move


###############################################################################
# Part 1, Question 5
###############################################################################
def part1_runner(games_file: str, word_set_file: str, max_guesses: int,
                 num_games: int, adversary_random: bool) -> None:
    """Create a game tree from the given file, and run num_games games with the configuration described below.

    The Guesser is a RandomTreeGuesser whose game tree is the one generated from games_file.
    The Adversary is a RandomAdversary if adversary_random is True, otherwise it is a RandomTreeAdversary
    using the SAME game tree as the Guesser.

    Each game uses the word set contained in word_set_file and has max_guesses as the maximum number of guesses.

    Preconditions:
        - games_file refers to a csv file in the format described on the assignment handout
        - word_set_file and max_guesses satisfy the preconditions of aw.run_games
        - num_games >= 1

    Implementation notes:
        - Your implementation MUST correctly call aw.run_games. You may choose
          the values for the optional arguments passed to the function.
        - aw.run_games has a lot of arguments! You might find it easier to use the "keyword argument"
          form of function call:

          aw.run_games(
              num_games=...,
              guesser=...,
              adversary=...,
              etc.
          )

    >>> part1_runner('data/games/guesser_wins.csv', 'data/words/official_wordle.txt', 4, 100, True)
    """
    game_tree = load_game_tree(games_file)

    set_guesser = RandomTreeGuesser(game_tree)

    if adversary_random:
        set_adversary = aw.RandomAdversary()

    else:
        set_adversary = RandomTreeAdversary(game_tree)

    aw.run_games(
        num_games=num_games,
        guesser=set_guesser,
        adversary=set_adversary,
        word_set_file=word_set_file,
        max_guesses=max_guesses
    )


if __name__ == '__main__':
    import doctest

    doctest.testmod(verbose=True)
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (In PyCharm, select the lines below and press Ctrl/Cmd + / to toggle comments.)
    # You can use "Run file in Python Console" to run PythonTA,
    # and then also test your methods manually in the console.
    # import python_ta
    #
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'extra-imports': ['a2_adversarial_wordle', 'a2_game_tree', 'random', 'csv'],
    #     'allowed-io': ['load_game_tree']
    # })

    # Sample call to part1_runner (you can change this, just keep it in the main block!)
    # When you're ready, try replacing the games_file with data/games/guesser_wins.csv.
    # We strongly recommend commenting out the @check_contracts decorator above GameTree
    # when running this function on the guesser_wins.csv dataset.
    # part1_runner(
    #     games_file='data/games/guesser_wins.csv',
    #     word_set_file='data/words/official_wordle.txt',
    #     max_guesses=4,
    #     num_games=100,
    #     adversary_random=False  # Try changing to False
    # )
