
deploy-test: clean
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/*

deploy-prod: clean
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/*

clean:
	- rm -rf *.egg-info build/ dist/
