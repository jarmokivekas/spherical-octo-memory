docs: clean
	# sphinx-apidoc -o docs/ roller
	python3 -m sphinx docs docs/_build

showdocs: docs
	firefox docs/_build/index

clean:
	rm -r docs/_build