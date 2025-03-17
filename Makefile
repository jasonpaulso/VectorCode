.PHONY: multitest

test:
	pdm lock --group dev; \
	pdm run pytest --enable-coredumpy --coredumpy-dir dumps

multitest:
	@for i in {11..13}; do \
		pdm use python3.$$i; \
		pdm lock --group dev; \
		pdm install; \
		make test; \
	done

