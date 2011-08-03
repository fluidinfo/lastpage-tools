.PHONY: lint pep8 pyflakes

lint: pep8 pyflakes

pep8:
	pep8 --repeat lastpage.py

pyflakes:
	pyflakes lastpage.py
