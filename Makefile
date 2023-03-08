# Define the Python files to format
PYTHON_FILES := $(shell find . -name "*.py" -not -path "./venv/*")

.PHONY: format

format:
	black $(PYTHON_FILES)
