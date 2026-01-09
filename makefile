RUFF := $(shell which ruff 2>/dev/null || echo uvx ruff)

all: lint clang-format ruff-format

lint:
	$(RUFF) check --fix

clang-format:
	find . -regex '.*\.\(cpp\|hpp\|cc\|cxx\|h\)' | xargs clang-format -i

ruff-format:
	$(RUFF) format
