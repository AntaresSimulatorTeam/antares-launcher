PYTHON   = /usr/bin/python3
VENV_DIR = venv

# help: help                           - display this makefile's help information
.PHONY: help
help:
	@grep "^# help\:" Makefile | grep -v grep | sed 's/\# help\: //' | sed 's/\# help\://'

# help: venv                           - create a virtual environment for development
.PHONY: venv
venv:
	@if [ -d "$(VENV_DIR)" ]; then rm -rf "$(VENV_DIR)"; fi
	@mkdir -p "$(VENV_DIR)"
	@$(PYTHON) -m venv "$(VENV_DIR)"
	@/bin/bash -c "source $(VENV_DIR)/bin/activate && python -m pip install --upgrade pip setuptools wheel"
	@printf "\nEnter virtual environment using:\n\nsource $(VENV_DIR)/bin/activate\n"

# help: req                            - install requirements
.PHONY: req
req:
	@/bin/bash -c "source $(VENV_DIR)/bin/activate \
	&& pip install pip --upgrade \
	&& pip install -r requirements.txt"

# help: binary                         - generate the binary file in the dist directory
.PHONY: binary
binary:
	@/bin/bash -c "source $(VENV_DIR)/bin/activate \
	&& pyinstaller -F antareslauncher/basic_launch.py -n Antares_Launcher"

# help: advanced_binary                - generate the advanced binary file in the dist directory
.PHONY: advanced_binary
advanced_binary:
	@/bin/bash -c "source $(VENV_DIR)/bin/activate \
	&& pyinstaller -F antareslauncher/advanced_launch.py -n Antares_Launcher_Advanced"

# help: clean                          - clean all files generated while compilation
.PHONY: clean
clean:
	rm -rf build/ dist/ antareslauncher/__pycache__ antareslauncher/hooks/__pycache__ __pycache__ $(VENV_DIR)

# help: test-all                       - run all tests
.PHONY: test-all
test-all:
	pytest

# help: test-unit                      - run unit tests
.PHONY: test-unit
test-unit:
	pytest -m unit_test

# help: test-integration               - run integration tests
.PHONY: test-integration
test-integration:
	pytest -m integration_test

# help: docs                            - generate documentation in doc/build
.PHONY: docs
docs:
	@/bin/bash -c "source $(VENV_DIR)/bin/activate \
	&& sphinx-apidoc -fMe -o doc/source/api antareslauncher/ -t doc/source/_templates/ \
	&& sphinx-build -b html -d build/docs/doctrees doc/source dist/docs/html"

# help: black                          - apply black to all .py files
.PHONY: black
black:
	find antareslauncher/ tests/ -name '*.py' -exec black {} \;

