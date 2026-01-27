.PHONY: fmt
fmt:
	isort setup.py src tests
	black .

.PHONY: fmt-travis
fmt-travis:
	isort --diff --check-only setup.py src tests
	black . --check

.PHONY: lint
lint:
	pylint setup.py
	pylint src/dbus_python_client_gen
	pylint tests --ignore=_introspect.py
	pyright

.PHONY: test
test:
	python3 -m unittest discover tests	

.PHONY: coverage
coverage:
	coverage --version
	coverage run --timid --branch -m unittest discover tests
	coverage report -m --fail-under=100 --show-missing --include="./src/*"

PYREVERSE_OPTS = --output=pdf
.PHONY: view
view:
	-rm -Rf _pyreverse
	mkdir _pyreverse
	PYTHONPATH=src pyreverse ${PYREVERSE_OPTS} --project="dbus-python-client-gen" src/dbus_python_client_gen
	mv classes_dbus-python-client-gen.pdf _pyreverse
	mv packages_dbus-python-client-gen.pdf _pyreverse

.PHONY: yamllint
yamllint:
	yamllint --strict .packit.yaml .github/workflows/main.yml

.PHONY: package
package:
	(umask 0022; python -m build; python -m twine check --strict ./dist/*)
