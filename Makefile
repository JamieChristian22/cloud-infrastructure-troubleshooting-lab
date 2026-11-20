.PHONY: install test demo serve status clean check
install:
	python -m pip install -e .
test:
	python -m unittest discover -s tests -v
check:
	python -m compileall -q src tests
	python -m unittest discover -s tests -v
demo:
	python -m cloudops_lab demo --output evidence
serve:
	python -m cloudops_lab serve
status:
	python -m cloudops_lab status
clean:
	rm -rf .lab build dist
