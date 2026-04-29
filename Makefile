# Variable Panel — Developer Makefile
# ─────────────────────────────────────────────────────────────────────────────
# Available targets:
#   make test              Run unit tests (no QGIS needed)
#   make test-docker       Run tests inside QGIS LTR Docker image
#   make test-docker-ltr   Same as above, explicit LTR tag
#   make test-docker-latest Run tests inside QGIS latest Docker image
#   make clean             Remove pytest cache and coverage files

PLUGIN_NAME   := variable_panel
QGIS_LTR      := qgis/qgis:release-3_34
QGIS_LATEST   := qgis/qgis:latest


.PHONY: test test-docker test-docker-ltr test-docker-latest clean

# ── Local (mocked) tests ────────────────────────────────────────────────────
test:
	pytest test/ -v --tb=short

# ── Docker integration tests ────────────────────────────────────────────────
test-docker: test-docker-ltr

test-docker-ltr:
	@echo "▶  Running tests inside $(QGIS_LTR)..."
	docker run --rm \
		-v "$(PWD):/src" \
		--user $(shell id -u):$(shell id -g) \
		$(QGIS_LTR) \
		bash /src/.docker/run-docker-tests.sh

test-docker-latest:
	@echo "▶  Running tests inside $(QGIS_LATEST)..."
	docker run --rm \
		-v "$(PWD):/src" \
		--user $(shell id -u):$(shell id -g) \
		$(QGIS_LATEST) \
		bash /src/.docker/run-docker-tests.sh

# ── Cleanup ─────────────────────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -f .coverage coverage.xml
