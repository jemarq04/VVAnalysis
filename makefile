RUFF := $(shell which ruff 2>/dev/null || echo uvx ruff)

clang-format:
	find . -regex '.*\.\(cpp\|hpp\|cc\|cxx\|h\)' | xargs clang-format -i

ruff-check:
	$(RUFF) check

ruff-format:
	$(RUFF) format
