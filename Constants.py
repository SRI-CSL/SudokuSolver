# The non-yices portions of this code base come from:
#
# http://newcoder.io/gui/
#
# where the license is:
#
# https://creativecommons.org/licenses/by-sa/3.0/deed.en_US
#
# I have modified the code as I saw fit to suit my purposes.
# All changes are recorded in the git commits.
#


# Available sudoku boards
BOARDS = ['debug', 'n00b', 'l33t', 'error']

# Pixels around the board
MARGIN = 20

# Width of every board cell.
SIDE = 50

# Width and height of the whole board
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 9
