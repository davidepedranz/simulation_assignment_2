.DEFAULT_GOAL := run
.PHONY: all process

run:
	@echo "Running simulations in parallel..."
	@echo ""
	@mkdir -p output
	@python simulator/main.py -l | shuf | parallel -j 7 --no-notice
	@echo ""
