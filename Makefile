
default: lint test

test:
	pytest .

lint:
	mypy daacla
	pycodestyle daacla

deploy-test: test clean
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/*

deploy-prod: test clean
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload --verbose dist/*

clean:
	- rm -rf *.egg-info build/ dist/
