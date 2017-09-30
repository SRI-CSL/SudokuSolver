# SudukoSolver

A simple sudoku puzzle solver using the new python bindings for yices.

## Prerequisites

You will need to install [yices](https://github.com/SRI-CSL/yices2) which can be done by building from source,
or using apt on linux (from our PPA) or homebrew on a mac, the readme there describes the process.

You will also need the python bindings:
```
pip install yices
```

## Usage

So not a lot of brain power was spent making this a watertight work. But if you start of with an empty board
```
./sudokusolver
```
you can add entries one by one, and then solve. Clear the solution and continue to add entries. Or if you wish you
can clear the entries too.  There are a couple of built in boards, so you can start from one like so:
```
./sudokusolver --board debug
./sudokusolver --board n00b
./sudokusolver --board l33t
```
add a few entries and then solve. Seems like the `l33t` board has 158 solutions, which I think means it is not a
legal puzzle.

You can also ask for the number of solutions, but if there are more than 64 we do not persist, and just return 64.

## Acknowledgments

This project was built on top of the nice python [tutorial](http://newcoder.io/gui/) by [Lynn Root](http://www.roguelynn.com/)
who is hereby thanked. The tutorial is under the creative commons [license](https://creativecommons.org/licenses/by-sa/3.0/deed.en_US) which does
not appear to be an option in GitHub's license widget, so if this is a problem let me know.
