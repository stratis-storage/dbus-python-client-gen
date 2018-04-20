TOX=tox

.PHONY: fmt
fmt:
	yapf --style pep8 --recursive --in-place check.py setup.py src tests

fmt-travis:
	yapf --style pep8 --recursive --diff check.py setup.py src tests

.PHONY: lint
lint:
	$(TOX) -c tox.ini -e lint

.PHONY: coverage
coverage:
	$(TOX) -c tox.ini -e coverage

.PHONY: test
test:
	$(TOX) -c tox.ini -e test

.PHONY: upload-release
upload-release:
	python setup.py register sdist upload

PYREVERSE_OPTS = --output=pdf
.PHONY: view
view:
	-rm -Rf _pyreverse
	mkdir _pyreverse
	PYTHONPATH=src pyreverse ${PYREVERSE_OPTS} --project="dbus-python-client-gen" src/dbus_python_client_gen
	mv classes_dbus-python-client-gen.pdf _pyreverse
	mv packages_dbus-python-client-gen.pdf _pyreverse
