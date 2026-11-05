.PHONY: preflight test reconcile outbox expire backup restore e2e lighthouse

PYTHON ?= python

preflight:
	cd apps/api && $(PYTHON) scripts/preflight.py

test:
	cd apps/api && $(PYTHON) -m pytest

reconcile:
	cd apps/api && $(PYTHON) scripts/reconcile.py

outbox:
	cd apps/api && $(PYTHON) scripts/dispatch_outbox.py

expire:
	cd apps/api && $(PYTHON) scripts/expire_orders.py

backup:
	cd apps/api && ./scripts/backup_db.sh

restore:
	@echo "Usage: make restore DUMP=backups/file.dump"
	cd apps/api && ./scripts/restore_db.sh "$(DUMP)"

e2e:
	npx playwright test

lighthouse:
	npm run lighthouse
