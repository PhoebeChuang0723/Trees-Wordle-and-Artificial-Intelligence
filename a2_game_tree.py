"""CSC111 Winter 2023 Assignment 3: Trees, Wordle, and Artificial Intelligence (Game Tree)

Instructions (READ THIS FIRST!)
===============================

This Python module contains the start of a GameTree class that you'll be working with
and modifying in this assignment. You WILL be submitting this file!

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2023 Mario Badr, David Liu, and Isaac Waller.
"""
from __future__ import annotations
from typing import Optional
# from typing import Any

# Comment out this line when you aren't using check_contracts
# from python_ta.contracts import check_contracts

GAME_START_MOVE = '*'


# === NOTE ABOUT USING check_contracts (PLEASE READ!) ===
# Because this assignment involves longer computations, we recommend commenting out @check_contracts
# on the line below when running your code on the larger word sets. Doing so will speed up the running
# time of the GameTree methods. However, when first testing your code on smaller examples
# (which you should definitely do!), we recommend keeping @check_contracts uncommented to take
# advantage of the representation invariants and preconditions we've provided you. 😊
# @check_contracts
class GameTree:
    """A decision tree for Adversarial Wordle moves.

    Each node in the tree stores an Adversarial Wordle move.

    Instance Attributes:
        - move: the current move (guess or status), or '*' if this tree represents the start of a game
        - guesser_win_probability: the probability that the Guesser will win from the current state of the game

    Representation Invariants:
        - self.move == GAME_START_MOVE or self.move is a valid Adversarial Wordle move
        - all(key == self._subtrees[key].move for key in self._subtrees)
        - GAME_START_MOVE not in self._subtrees  # since it can only appear at the very top of a game tree
        - 0.0 <= guesser_win_probability <= 1.0
    """
    move: str | tuple[str, ...]  # The vertical bar | means "or"
    guesser_win_probability: float

    # Private Instance Attributes:
    #  - _subtrees:
    #      the subtrees of this tree, which represent the game trees after a possible
    #      move by the current player. Unlike the Tree representation in lecture,
    #      this collection is a MAPPING where the values are GameTrees, and associated
    #      keys are the moves at the root of each subtree. See the last representation
    #      invariant above.
    _subtrees: dict[str | tuple[str, ...], GameTree]

    def __init__(self, move: str | tuple[str, ...] = GAME_START_MOVE, guesser_win_probability: float = 0.0) -> None:
        """Initialize a new game tree.

        Note that this initializer uses optional arguments.

        >>> game = GameTree()
        >>> game.move == GAME_START_MOVE
        True
        """
        self.move = move
        self.guesser_win_probability = guesser_win_probability
        self._subtrees = {}

    def get_subtrees(self) -> list[GameTree]:
        """Return the subtrees of this game tree."""
        return list(self._subtrees.values())

    def find_subtree_by_move(self, move: str | tuple[str, ...]) -> Optional[GameTree]:
        """Return the subtree corresponding to the given move.

        Return None if no subtree corresponds to that move.
        """
        if move in self._subtrees:
            return self._subtrees[move]
        else:
            return None

    def is_guesser_turn(self) -> bool:
        """Return whether the NEXT move should be made by the Guesser."""
        return self.move == GAME_START_MOVE or isinstance(self.move, tuple)

    def __len__(self) -> int:
        """Return the number of items in this tree."""
        # Note: no "empty tree" base case is necessary here.
        # Instead, the only implicit base case is when there are no subtrees (sum returns 0).
        return 1 + sum(subtree.__len__() for subtree in self._subtrees.values())

    def __str__(self) -> str:
        """Return a string representation of this tree.
        """
        return self._str_indented(0)

    def _str_indented(self, depth: int) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.

        You MAY change the implementation of this method (e.g. to display different instance attributes)
        as you work on this assignment.

        Preconditions:
            - depth >= 0
        """
        if self.is_guesser_turn():
            turn_desc = "Guesser's move"
        else:
            turn_desc = "Adversary's move"
        move_desc = f'{self.move} -> {turn_desc}\n'
        str_so_far = '  ' * depth + move_desc
        for subtree in self._subtrees.values():
            str_so_far += subtree._str_indented(depth + 1)
        return str_so_far

    def add_subtree(self, subtree: GameTree) -> None:
        """Add a subtree to this game tree."""
        self._subtrees[subtree.move] = subtree
        self._update_guesser_win_probability()

    ############################################################################
    # Part 1: Loading and "Replaying" Adversarial Wordle games
    ############################################################################
    def insert_move_sequence(self, moves: list[str | tuple[str, ...]], guesser_win_probability: float = 0.0) -> None:
        """Insert the given sequence of moves into this tree.

        The inserted moves form a chain of descendants, where:
            - moves[0] is a child of this tree's root
            - moves[1] is a child of moves[0]
            - moves[2] is a child of moves[1]
            - etc.

        Do not create duplicate moves that share the same parent; for example, if moves[0] is
        already a child of this tree's root, you should recurse into that existing subtree rather
        than create a new subtree with moves[0].
        But if moves[0] is not a child of this tree's root, create a new subtree for it
        and add it to the existing collection of subtrees.

        Preconditions:
        - moves alternates between str and tuple[str, ...] elements
        - if self.move == aw.GAME_START_MOVE or isinstance(self.move, tuple), \
        then moves == [] or isinstance(moves[0], str)
        - if self.move != aw.GAME_START_MOVE and isinstance(self.move, str), \
        then moves == [] or isinstance(moves[0], tuple)


        Implementation Notes:
            - Your implementation must use recursion, and NOT use any loops to "go down" the tree.
                - "Using recursion" also includes calling a recursive helper method, like GameTree__str__.
            - Your implementation must have a worst-case running time of Theta(m) time, where m is
              the length of moves. This means you shouldn't use list slicing to access the "rest" of
              the list of moves, like in Tutorial 4. Instead, you can use one of the following approaches:

              i) Use a recursive helper method that takes an extra "current index" argument to
                 keep track of the next move in the list to add.
              ii) First reverse the list, and then use a recursive helper method that calls
                 `list.pop` on the list of moves. Just make sure the original list isn't changed
                 when the function ends!

        >>> game_tree = GameTree(GAME_START_MOVE)
        >>> sub1 = GameTree('reach')
        >>> sub2 = GameTree(('?', 'N', 'Y', 'N', 'N'))
        >>> sub2.add_subtree(GameTree('brawl'))
        >>> sub1.add_subtree(sub2)
        >>> game_tree.add_subtree(sub1)
        >>> given_moves = ['reach', ('?', 'N', 'Y', 'N', 'N'), 'quart']
        >>> game_tree.insert_move_sequence(given_moves)
        >>> print(game_tree)
        * -> Guesser's move
         reach -> Adversary's move
            ('?', 'N', 'Y', 'N', 'N') -> Guesser's move
                brawl -> Adversary's move
                quart -> Adversary's move
        """
        self._check_tree(moves, 0, guesser_win_probability)

    def _check_tree(self, given_moves: list[str | tuple[str, ...]], curr_index: int,
                    guesser_win_probability: float) -> None:
        """Check whether the subtrees contain the item in moves.
        If the item is not in the subtrees, add a new subtree containing the item.
        If the item is in the subtrees, recurse into the subtree containing the item.
        """
        if curr_index <= len(given_moves) - 1:
            item = given_moves[curr_index]

            if item not in self._subtrees:
                subtree = GameTree(item)
                self.add_subtree(subtree)
                subtree.guesser_win_probability = guesser_win_probability
                # self.add_subtree(GameTree(item))
                # self.find_subtree_by_move(item).guesser_win_probability = guesser_win_probability

            self._subtrees[item]._check_tree(given_moves, curr_index + 1, guesser_win_probability)

    ############################################################################
    # Part 2: Complete Game Trees and Win Probabilities
    ############################################################################
    def _update_guesser_win_probability(self) -> None:
        """Recalculate the guesser win probability of this tree.

        Note: like the "_length" Tree attribute from tutorial, you should only need
        to update self here, not any of its subtrees. (You should *assume* that each
        subtree has the correct guesser win probability already.)

        Use the following definition for the guesser win probability of self:
            - if self is a leaf, don't change the guesser win probability
              (leave the current value alone)
            - if self is not a leaf and self.is_guesser_turn() is True, the guesser win probability
              is equal to the MAXIMUM of the guesser win probabilities of its subtrees
            - if self is not a leaf and self.is_guesser_move is False, the guesser win probability
              is equal to the AVERAGE of the guesser win probabilities of its subtrees
        """
        subtree_win_probs = [subtree.guesser_win_probability for subtree in self.get_subtrees()]

        if self._subtrees == {}:
            pass
        elif self.is_guesser_turn():
            self.guesser_win_probability = max(subtree_win_probs)
        else:
            self.guesser_win_probability = sum(subtree_win_probs) / len(subtree_win_probs)


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
    #     'max-line-length': 120
    # })
