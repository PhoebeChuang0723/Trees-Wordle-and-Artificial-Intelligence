"""CSC111 Winter 2023 Assignment 2: Trees, Wordle, and Artificial Intelligence (Part 2)

Instructions (READ THIS FIRST!)
===============================

This Python module contains the start of functions and/or classes you'll define
for Part 2 of this assignment. Please note that in addition to this file, you will
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
import random
from typing import Optional

import a2_game_tree
import a2_adversarial_wordle as aw


def generate_complete_game_tree(root_move: str | tuple[str, ...], game_state: aw.AdversarialWordle,
                                d: int) -> a2_game_tree.GameTree:
    """Generate a complete game tree of depth d for all valid moves from the current game_state.

    For the returned GameTree:
        - Its root move is root_move.
        - It contains all possible move sequences of length <= d from game_state.
        - If d == 0, a size-one GameTree is returned.

    Note that some paths down the tree may have length < d, because they result in a game state
    with a winner in fewer than d moves. Concretely, if game_state.get_winner() is not None,
    then return just a size-one GameTree containing the root move.

    Preconditions:
        - d >= 0
        - root_move == a2_game_tree.GAME_START_MOVE or root_move is a valid move
        - if root_move == a2_game_tree.GAME_START_MOVE, then game_state is in the initial game state
        - if isinstance(root_move, str) and root_move != a2_game_tree.GAME_START_MOVE,\
            then (game_state.guesses[-1] == root_move) and (not game_state.is_guesser_turn())
        - if isinstance(root_move, tuple),\
            then (game_state.statuses[-1] == root_move) and game_state.is_guesser_turn()

    We have provided some small doctest examples here. You may add your own, and we encourage you to test
    this function thoroughly before moving on.

    >>> example_game = aw.AdversarialWordle({'hello', 'words', 'world'}, 3)
    >>> tree0 = generate_complete_game_tree(a2_game_tree.GAME_START_MOVE, example_game, 0)
    >>> len(tree0)
    1
    >>> tree1 = generate_complete_game_tree(a2_game_tree.GAME_START_MOVE, example_game, 1)
    >>> len(tree1)
    4
    >>> sorted([subtree.move for subtree in tree1.get_subtrees()])  # Ignore any PyCharm warning about "subtree"
    ['hello', 'words', 'world']
    >>> tree2 = generate_complete_game_tree(a2_game_tree.GAME_START_MOVE, example_game, 2)
    >>> len(tree2)
    10
    >>> tree3 = generate_complete_game_tree(a2_game_tree.GAME_START_MOVE, example_game, 3)
    >>> len(tree3)
    16
    >>> tree_hello = generate_complete_game_tree('hello', example_game, 3)
    >>> len(tree_hello)
    7
    Implementation hints:
        - This function must be implemented recursively.
        - In the recursive step, use the AdversarialWordle's copy_and_record_guesser_move/
          copy_and_record_adversary_move methods to create a copy of the game_state with one new move made.
          You should NOT mutate the input game_state in this function.
        - You'll need to review the public interface of the AdversarialWordle class to see what
          methods are available to help implement this function.
        - Remember that the Guesser can only choose guesses from the current possible answers,
          which may be significantly fewer than the full word set. This is important for making
          sure your game tree isn't larger than it should be!
    """
    if game_state.is_guesser_turn() and isinstance(root_move, str) and root_move != a2_game_tree.GAME_START_MOVE:
        new_game_state = game_state.copy_and_record_guesser_move(root_move)
        return generate_complete_game_tree(root_move, new_game_state, d)

    tree_created = a2_game_tree.GameTree(root_move)

    if game_state.get_winner() == 'Guesser':
        tree_created.guesser_win_probability = 1.0
    else:
        tree_created.guesser_win_probability = 0.0

    if d == 0 or game_state.get_winner() is not None:
        return tree_created

    else:
        if not game_state.is_guesser_turn():
            possible_answers = game_state.get_possible_answers()
            current_guess = game_state.guesses[-1]
            if len(possible_answers) > 1:
                possible_answers.remove(current_guess)

            for possible_ans in possible_answers:
                curr_move = game_state.get_status_for_answer(possible_ans)
                new_game_state = game_state.copy_and_record_adversary_move(curr_move)
                subtree = generate_complete_game_tree(curr_move, new_game_state, d - 1)
                tree_created.add_subtree(subtree)

        else:
            for possible_ans in game_state.get_possible_answers():
                curr_move = possible_ans
                new_game_state = game_state.copy_and_record_guesser_move(curr_move)
                subtree = generate_complete_game_tree(curr_move, new_game_state, d - 1)
                tree_created.add_subtree(subtree)

        return tree_created


class GreedyTreeGuesser(aw.Guesser):
    """An Adversarial Wordle Guesser that plays greedily based on a given GameTree.

    See assignment handout for description of its strategy.
    """
    # Private Instance Attributes:
    #   - _game_tree:
    #       The GameTree that this player uses to make its moves. If None, then this
    #       player just makes random moves.
    _game_tree: Optional[a2_game_tree.GameTree]

    def __init__(self, game_tree: a2_game_tree.GameTree) -> None:
        """Initialize this player.

        Preconditions:
            - game_tree.move == a2_game_tree.GAME_START_MOVE
        """
        self._game_tree = game_tree

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
            subtrees = self._game_tree.get_subtrees()
            max_prob = 0.0
            max_prob_subtree = None

            for subtree in subtrees:
                if subtree.guesser_win_probability >= max_prob:
                    max_prob = subtree.guesser_win_probability
                    max_prob_subtree = subtree

            self._game_tree = max_prob_subtree
            return max_prob_subtree.move


class GreedyTreeAdversary(aw.Adversary):
    """An Adversarial Wordle Adversary that plays greedily based on a given GameTree.

    See assignment handout for description of its strategy.
    """
    # Private Instance Attributes:
    #   - _game_tree:
    #       The GameTree that this player uses to make its moves. If None, then this
    #       player just makes random moves.
    _game_tree: Optional[a2_game_tree.GameTree]

    def __init__(self, game_tree: a2_game_tree.GameTree) -> None:
        """Initialize this player.

        Preconditions:
            - game_tree.move == a2_game_tree.GAME_START_MOVE
        """
        self._game_tree = game_tree

    def make_move(self, game: aw.AdversarialWordle) -> tuple[str, ...]:
        """Make a move given the current game.

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
            subtrees = self._game_tree.get_subtrees()
            min_prob = 1.0
            min_prob_subtree = None

            for subtree in subtrees:
                if subtree.guesser_win_probability <= min_prob:
                    min_prob = subtree.guesser_win_probability
                    min_prob_subtree = subtree

            self._game_tree = min_prob_subtree
            return min_prob_subtree.move


def part2_runner(word_set_file: str, max_guesses: int, depth: int, num_games: int, guesser_greedy: bool) -> None:
    """Create a complete game tree with the given depth, and run num_games games using the following game configuration.

    If guesser_greedy is True, the Guesser player is the GreedyTreeGuesser and the Adversary is a RandomAdversary.
    If guesser_greedy is False, the Guesser player is a RandomGuesser and the Adversary is a GreedyTreeAdversary.

    In either case, the "Greedy Tree" player uses the complete game tree with the given depth.

    word_set_file and max_guesses have the same meaning as in aw.run_games.

    Preconditions:
        - word_set_file and max_guesses satisfy the preconditions of aw.run_games
        - depth >= 0
        - num_games >= 1

    Implementation notes:
        - Your implementation MUST correctly call aw.run_games. You may choose
          the values for the optional arguments passed to the function.
    """
    with open(word_set_file) as f:
        word_set = {str.strip(line.lower()) for line in f}

    game = aw.AdversarialWordle(word_set, max_guesses)
    complete_game_tree = generate_complete_game_tree(a2_game_tree.GAME_START_MOVE, game, depth)

    if guesser_greedy:
        guesser = GreedyTreeGuesser(complete_game_tree)
        adversary = aw.RandomAdversary()

    else:
        guesser = aw.RandomGuesser()
        adversary = GreedyTreeAdversary(complete_game_tree)

    aw.run_games(
        num_games=num_games,
        guesser=guesser,
        adversary=adversary,
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

    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'max-nested-blocks': 4,
    #     'extra-imports': ['random', 'a2_adversarial_wordle', 'a2_game_tree'],
    #     'allowed-io': ['part2_runner']
    # })

    # Sample call to part2_runner (you can change this, just keep it in the main block!)
    # We recommend commenting out the @check_contracts decorator for both GameTree
    # and AdversarialWordle.
    # part2_runner(
    #     word_set_file='data/words/official_wordle_25.txt',
    #     max_guesses=3,
    #     depth=6,  # A complete game tree for 3 rounds
    #     num_games=100,
    #     guesser_greedy=True
    # )
