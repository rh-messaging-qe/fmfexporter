MODULE=fmfexporter

all: clean build pip-install
.PHONY: clean build

# Python packaging
build:
	python3 setup.py bdist_wheel

pip-uninstall:
	pip3 uninstall -y $(MODULE)
	
pip-install:
	pip3 install --force dist/*.whl
	
unittest:
	python3 setup.py test

upload:
	twine upload dist/*.whl

clean:
	python setup.py clean
	rm -rf build dist fmfexporter.egg-info .eggs
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
