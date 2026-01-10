PRECOMMIT := $(shell which pre-commit 2>/dev/null || echo uvx pre-commit)

.PHONY: lint

lint:
	$(PRECOMMIT) run -a
