"""CSC111 Winter 2023 Assignment 2: Trees, Wordle, and Artificial Intelligence (Part 3)

Instructions (READ THIS FIRST!)
===============================

This Python module contains the start of functions and/or classes you'll define
for Part 3 of this assignment. You should NOT make any changes to a2_adversarial_wordle.py.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2023 Mario Badr, David Liu, and Isaac Waller.
"""
import random
from typing import Optional

import a2_game_tree
import a2_adversarial_wordle as aw


class ExploringGuesser(aw.Guesser):
    """A Guesser player that sometimes plays greedily and sometimes plays randomly.

    See assignment handout for details.

    Representation Invariants:
        - 0.0 <= self._exploration_probability <= 1.0
    """
    # Private Instance Attributes:
    #   - _game_tree:
    #       The GameTree that this player uses to make its moves. If None, then this
    #       player just makes random moves.
    #   - _exploration_probability:
    #       The probability that this player ignores its game tree and makes a random move.
    _game_tree: Optional[a2_game_tree.GameTree]
    _exploration_probability: float

    def __init__(self, game_tree: a2_game_tree.GameTree, exploration_probability: float) -> None:
        """Initialize this player."""
        self._game_tree = game_tree
        self._exploration_probability = exploration_probability

    def make_move(self, game: aw.AdversarialWordle) -> str:
        """Make a move given the current game.

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
            return random.choice(possible_answers)

        else:
            x = random.uniform(0.0, 1.0)

            if x < self._exploration_probability:
                possible_answers = game.get_possible_answers()
                answer = random.choice(possible_answers)
                answer_subtree = self._game_tree.find_subtree_by_move(answer)

                if answer_subtree not in self._game_tree.get_subtrees():
                    self._game_tree = None

                else:
                    self._game_tree = answer_subtree

                return answer

            else:
                subtrees = self._game_tree.get_subtrees()
                max_prob = 0.0
                max_prob_subtree = None

                for subtree in subtrees:
                    if subtree.guesser_win_probability >= max_prob:
                        max_prob = subtree.guesser_win_probability
                        max_prob_subtree = subtree

                self._game_tree = max_prob_subtree
                return max_prob_subtree.move


def run_learning_algorithm(
        word_set_file: str,
        max_guesses: int,
        exploration_probabilities: list[float],
        show_stats: bool = True) -> a2_game_tree.GameTree:
    """Play a sequence of AdversarialWordle games using an ExploringGuesser and RandomAdversary.

    This algorithm first initializes an empty GameTree. All ExploringGuessers will use this
    SAME GameTree object, which will be mutated over the course of the algorithm!
    Return this object.

    There are len(exploration_probabilities) games played, where at game i (starting at 0):
        - The Guesser is an ExploringGuesser (using the game tree) whose exploration probability
            is equal to exploration_probabilities[i].
        - The Adversary is a RandomAdversary.
        - AFTER the game, the move sequence from the game is inserted into the game tree,
          with a guesser win probability of 1.0 if the Guesser won the game, and 0.0 otherwise.

    Preconditions:
        - word_set_file and max_guesses satisfy the preconditions of aw.run_game
        - all(0.0 <= p <= 1.0 for p in exploration_probabilities)
        - exploration_probabilities != []

    Implementation notes:
        - A NEW ExploringGuesser instance should be created for each loop iteration.
          However, each one should use the SAME GameTree object.
        - You should call aw.run_game, NOT aw.run_games. This is because you need more control
          over what happens after each game runs, which you can get by writing your own loop
          that calls run_game. However, you can base your loop on the implementation of run_games.
        - Note that aw.run_game returns the AdversarialWordle game instance. You may need to review
          the documentation for that class to figure out what methods are useful here.
        - You may call print in this function to report progress made in each game.
        - This function must return the final GameTree object. You can inspect the
          guesser_win_probability of its nodes, calculate its size, or use it in a
          RandomTreeGuesser or GreedyTreeGuesser to see how they do with it.
    """
    game_tree = a2_game_tree.GameTree()
    num_games = len(exploration_probabilities)
    stats = {'Guesser': 0, 'Adversary': 0}
    results = []

    for i in range(0, num_games):
        probability = exploration_probabilities[i]
        guesser = ExploringGuesser(game_tree, probability)
        adversary = aw.RandomAdversary()

        game = aw.run_game(guesser, adversary, word_set_file, max_guesses)

        winner = game.get_winner()
        stats[winner] += 1
        results.append(winner)

        sequence = game.get_move_sequence()
        if winner == 'Guesser':
            game_tree.insert_move_sequence(sequence, 1.0)
        else:
            game_tree.insert_move_sequence(sequence)

        print(stats)

    if show_stats:
        aw.plot_game_statistics(results)

    return game_tree


def part3_runner() -> a2_game_tree.GameTree:
    """Run example for Part 3.

    Please note that unlike part1_runner and part2_runner, this function is NOT tested.
    We encourage you to experiment with different exploration probability sequences
    to see how quickly you can develop a "winning" GameTree!
    """
    word_set_file = 'data/words/official_wordle_100.txt'
    max_guesses = 4
    probabilities = [0.5] * 1000

    return run_learning_algorithm(word_set_file, max_guesses, probabilities, show_stats=True)


if __name__ == '__main__':
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (In PyCharm, select the lines below and press Ctrl/Cmd + / to toggle comments.)
    # You can use "Run file in Python Console" to run PythonTA,
    # and then also test your methods manually in the console.
    # import python_ta
    #
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'max-nested-blocks': 4,
    #     'extra-imports': ['random', 'a2_adversarial_wordle', 'a2_game_tree'],
    #     'allowed-io': ['run_learning_algorithm']
    # })

    part3_runner()
