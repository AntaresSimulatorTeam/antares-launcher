PYTHON   = /usr/bin/python3
VENV_DIR = venv3.7

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

# help: test-end-to-end                - run end to end tests
.PHONY: test-end-to-end
test-end-to-end:
	pytest -m end_to_end_test

# help: doc                            - generate documentation in doc/build
.PHONY: doc
doc:
	@/bin/bash -c "source $(VENV_DIR)/bin/activate \
	&& cd doc \
	&& sphinx-apidoc -fMe -o source/ ../antareslauncher/ -t source/_templates/ \
	&& sphinx-build -b html ./source ./build"

# help: black                          - apply black to all .py files
.PHONY: black
black:
	find antareslauncher/ tests/ -name '*.py' -exec black {} \;

