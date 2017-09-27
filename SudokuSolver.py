
from ctypes import c_int32

"""
#this way is a bit long winded
from yices import (yices_init,
                   yices_exit,
                   yices_int_type,
                   yices_int32,
                   term_t,
                   type_t,
                   make_term_array,
                   make_type_array,
                   yices_distinct,
                   yices_and2,
                   yices_arith_eq_atom,
                   yices_arith_leq_atom,
                   yices_new_uninterpreted_term,
                   yices_new_config,
                   yices_new_context,
                   yices_default_config_for_logic,
                   yices_assert_formula,
                   yices_check_context,
                   yices_push,
                   yices_pop,
                   yices_get_model,
                   yices_free_model,
                   yices_get_int32_value,
                   yices_free_context,
                   yices_free_config)
"""

#this way we could use the yices_ prefixes everywhere and feel safe.
from yices import *

from SudokuBoard import SudokuBoard


class SudokuSolver(object):

    """
    The Sudoku Solver, will solve when asked.

    iam: haven't really thought about the UI yet.


    """
    def __init__(self, game):
        self.game = game
        yices_init()
        # the matrix of uninterpreted terms
        self.variables = self.__createVariables()
        # the numerals as yices constants
        self.numerals = self.__createNumerals()
        # the yices configuration for puzzle solving
        self.config = yices_new_config()
        # is push and pop the default (yes; had to look at the source though.)
        yices_default_config_for_logic(self.config, "QF_LIA")
        # the context (a set/stack of yices assertions)
        self.context = yices_new_context(self.config)
        # add the generic constraints (corresponding to the rules of the game)
        self.__generateConstraints()


    # would take some (unnecessary) effort to hook these in somewhere
    def __cleanUp(self):
        yices_free_context(self.context)
        yices_free_config(self.config)
        yices_exit()


    def __createVariables(self):
        """Creates the matrix of uninterpreted terms that represents the logical view of the board."""
        int_t = yices_int_type()
        variables = SudokuBoard.newBoard()
        for i in xrange(9):
            for j in xrange(9):
                variables[i][j] = yices_new_uninterpreted_term(int_t)
        return variables

    def __createNumerals(self):
        """Creates a mappimng from digits to yices constants for those digits."""
        numerals = {}
        for i in xrange(1, 10):
            numerals[i] = yices_int32(i)
        return numerals


    def __generateConstraints(self):
        one = self.numerals[1]
        nine = self.numerals[9]


        # each x is between 1 and 9
        def between_1_and_9(x):
            return yices_and2(yices_arith_leq_atom(one, x), yices_arith_leq_atom(x, nine))
        for i in xrange(9):
            for j in xrange(9):
                yices_assert_formula(self.context, between_1_and_9(self.variables[i][j]))

        # all elements of the array x are distinct
        def all_distinct(x):
            n = len(x)
            a = make_term_array(x)
            return yices_distinct(n, a)

        # All elements in a row must be distinct
        for i in xrange(9):
            yices_assert_formula(self.context, all_distinct([self.variables[i][j] for j in xrange(9)]))  #I.e.  all_distinct(X[i])


        # All elements in a column must be distinct
        for i in xrange(9):
            yices_assert_formula(self.context, all_distinct([self.variables[j][i] for j in xrange(9)]))

        # All elements in each 3x3 square must be distinct
        for k in xrange(3):
            for l in xrange(3):
                yices_assert_formula(self.context, all_distinct([self.variables[i + 3 * l][j + 3 * k] for i in xrange(3) for j in xrange(3)]))


    def __addFacts(self):
        """Adds the facts gleaned from the current state of the puzzle."""
        def set_value(row, column, value):
            assert 0 <= row and row < 9
            assert 0 <= column and column < 9
            assert 1 <= value and value <= 9
            yices_assert_formula(self.context, yices_arith_eq_atom(self.variables[row][column], self.numerals[value]))


        for i in xrange(9):
            for j in xrange(9):
                value = self.game.puzzle[i][j]
                if value != 0:
                    set_value(i, j, value)


    def solve(self):
        """Attempts to solve the puzzle, returning either None if there is no solution, or a board with the correct MISSING entries."""
        solution = None

        #we use push and pop so that we can solve (variants) repeatedly without having to start from scratch each time.
        yices_push(self.context)

        self.__addFacts()

        smt_stat = yices_check_context(self.context, None)

        if smt_stat != 3:
            print 'No solution: smt_stat = {0}\n'.format(smt_stat)
        else:
            #print model
            model = yices_get_model(self.context, 1)
            val = c_int32()

            #return the model as a board with ONLY the newly found values inserted.
            solution = SudokuBoard.newBoard()

            for i in xrange(9):
                for j in xrange(9):
                    if self.game.puzzle[i][j] == 0:
                        yices_get_int32_value(model, self.variables[i][j], val)
                        #print 'V({0}, {1}) = {2}'.format(i, j, val.value)
                        solution[i][j] = val.value

            yices_free_model(model)

        yices_pop(self.context)

        return solution
