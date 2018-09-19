
from SudokuBoard import SudokuBoard

from Constants import ALEPH_NOUGHT

from yices.Types import Types

from yices.Terms import Terms

from yices.Config import Config

from yices.Context import Context

from yices.Status import Status

from yices.Model import Model

from yices.Yices import Yices


class SudokuSolver(object):

    """
    The Sudoku Solver, will solve when asked.

    iam: haven't really thought about the UI yet.


    """
    def __init__(self, game):
        self.game = game
        # the matrix of uninterpreted terms
        self.variables = self.__createVariables()
        # the numerals as yices constants
        self.numerals = self.__createNumerals()
        # the yices configuration for puzzle solving
        self.config = Config()
        # is push and pop the default (yes; had to look at the source though.)
        self.config.default_config_for_logic("QF_LIA")
        # the context (a set/stack of yices assertions)
        self.context = Context(self.config)
        # add the generic constraints (corresponding to the rules of the game)
        self.__generateConstraints()


    # would take some (unnecessary) effort to hook these in somewhere
    def __cleanUp(self):
        self.context.dispose()
        self.config.dispose()
        Yices.exit()


    def __createVariables(self):
        """Creates the matrix of uninterpreted terms that represents the logical view of the board."""
        int_t = Types.int_type()
        variables = SudokuBoard.newBoard()
        for i in xrange(9):
            for j in xrange(9):
                variables[i][j] = Terms.new_uninterpreted_term(int_t)
        return variables

    def __createNumerals(self):
        """Creates a mapping from digits to yices constants for those digits."""
        numerals = {}
        for i in xrange(1, 10):
            numerals[i] = Terms.integer(i)
        return numerals


    def __generateConstraints(self):
        # each x is between 1 and 9
        def between_1_and_9(x):
            return Terms.disjunction([Terms.eq(x, self.numerals[i+1]) for i in xrange(9)])
        for i in xrange(9):
            for j in xrange(9):
                self.context.assert_formula(between_1_and_9(self.variables[i][j]))

        # All elements in a row must be distinct
        for i in xrange(9):
            self.context.assert_formula(Terms.distinct([self.variables[i][j] for j in xrange(9)]))


        # All elements in a column must be distinct
        for i in xrange(9):
            self.context.assert_formula(Terms.distinct([self.variables[j][i] for j in xrange(9)]))

        # All elements in each 3x3 square must be distinct
        for k in xrange(3):
            for l in xrange(3):
                self.context.assert_formula(Terms.distinct([self.variables[i + 3 * l][j + 3 * k] for i in xrange(3) for j in xrange(3)]))


    def __addFacts(self):
        """Adds the facts gleaned from the current state of the puzzle."""
        def set_value(row, column, value):
            assert 0 <= row and row < 9
            assert 0 <= column and column < 9
            assert 1 <= value and value <= 9
            self.context.assert_formula(Terms.arith_eq_atom(self.variables[row][column], self.numerals[value]))


        for i in xrange(9):
            for j in xrange(9):
                value = self.game.puzzle[i][j]
                if value != 0:
                    set_value(i, j, value)
    def solve(self):

        """Attempts to solve the puzzle, returning either None if there is no solution, or a board with the correct MISSING entries."""
        solution = None

        #we use push and pop so that we can solve (variants) repeatedly without having to start from scratch each time.
        self.context.push()

        self.__addFacts()

        smt_stat = self.context.check_context(None)

        if smt_stat != Status.SAT:
            print 'No solution: smt_stat = {0}\n'.format(smt_stat)
        else:
            #get the model
            model = Model.from_context(self.context, 1)

            #return the model as a board with ONLY the newly found values inserted.
            solution = SudokuBoard.newBoard()

            for i in xrange(9):
                for j in xrange(9):
                    if self.game.puzzle[i][j] == 0:
                        solution[i][j] = model.get_value(self.variables[i][j])

            model.dispose()

        self.context.pop()

        return solution

    #we could contrast the following with the  yices_assert_blocking_clause

    def countModels(self):

        def model2term(model):
            termlist = []
            for i in xrange(9):
                for j in xrange(9):
                    if self.game.puzzle[i][j] == 0:
                        val = model.get_value(self.variables[i][j])
                        var = self.variables[i][j]
                        value = self.numerals[val]
                        termlist.append(Terms.arith_eq_atom(var, value))
            return Terms.conjunction(termlist)

        result = 0

        self.context.push()

        self.__addFacts()

        while  self.context.check_context(None) == Status.SAT:
            model = Model.from_context(self.context, 1)
            diagram = model2term(model)
            self.context.assert_formula(Terms.negation(diagram))
            model.dispose()
            result += 1
            if result == ALEPH_NOUGHT:
                break

        self.context.pop()

        return result
