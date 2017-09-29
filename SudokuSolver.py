
from ctypes import c_int32

from yices import *

from SudokuBoard import SudokuBoard

from Constants import ALEPH_NOUGHT

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
        """Creates a mapping from digits to yices constants for those digits."""
        numerals = {}
        for i in xrange(1, 10):
            numerals[i] = yices_int32(i)
        return numerals


    def __generateConstraints(self):
        # each x is between 1 and 9
        def between_1_and_9(x):
            t = make_empty_term_array(9);
            for i in xrange(9):
                t[i] = yices_eq(x, self.numerals[i+1])
            return yices_or(9, t)
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
            yices_assert_formula(self.context, all_distinct([self.variables[i][j] for j in xrange(9)]))


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

        if smt_stat != STATUS_SAT:
            print 'No solution: smt_stat = {0}\n'.format(smt_stat)
        else:
            #get the model
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

    #we could contrast the following with the  yices_assert_blocking_clause

    def countModels(self):

        def model2term(model):
            termlist = []
            val = c_int32()
            for i in xrange(9):
                for j in xrange(9):
                    if self.game.puzzle[i][j] == 0:
                        yices_get_int32_value(model, self.variables[i][j], val)
                        var = self.variables[i][j]
                        value = self.numerals[val.value]
                        termlist.append(yices_arith_eq_atom(var, value))
            return yices_and(len(termlist), make_term_array(termlist))

        result = 0

        yices_push(self.context)

        self.__addFacts()

        while  yices_check_context(self.context, None) == STATUS_SAT:
            model = yices_get_model(self.context, 1)
            diagram = model2term(model)
            yices_assert_formula(self.context, yices_not(diagram))
            yices_free_model(model)
            result += 1
            if result == ALEPH_NOUGHT:
                break

        yices_pop(self.context)

        return result
