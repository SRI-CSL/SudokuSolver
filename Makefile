#iam's makefile; maybe migrate some targets to the main Makefile when done.

all: help


help:
	@echo ''
	@echo 'Here are the targets:'
	@echo ''
	@echo 'To run debug           :    "make debug"'
	@echo 'To run l33t            :    "make l33t"'
	@echo 'To run error           :    "make error"'
	@echo 'To pylint (errors)     :    "make lint"'
	@echo 'To pylint (all)        :    "make lint_all"'
	@echo ''

debug:
	./sudokusolver --board debug

l33t:
	./sudokusolver --board l33t

error:
	./sudokusolver --board error



clean:
	rm -f  *.pyc *~

PYLINT = $(shell which pylint)


check_lint:
ifeq ($(PYLINT),)
	$(error lint target requires pylint)
endif


lint: check_lint
# for detecting just errors:
	@ $(PYLINT) -E  *.py

lint_all: check_lint
# for detecting more than just errors:
	@ $(PYLINT) --rcfile=.pylintrc *.py

.PHONY: lint check_lint
