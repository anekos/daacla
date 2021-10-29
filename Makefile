
deploy-test:
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/*
