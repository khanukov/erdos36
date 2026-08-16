PYTHON ?= python3

.PHONY: check verify-central verify-central-128 fetch-upstream verify-outer verify-composite verify paper arxiv checksums release-candidate

check:
	$(PYTHON) scripts/check_repo.py
	$(PYTHON) scripts/verify_checksums.py

verify-central:
	bash verifier/run_central_check.sh

verify-central-128:
	MPFR_PREC=128 bash verifier/run_central_check.sh

fetch-upstream:
	$(PYTHON) upstream/fetch_upstream.py

verify-outer: fetch-upstream
	$(PYTHON) upstream/verify_outer_bins.py

verify-composite:
	bash scripts/verify_all.sh

verify: check
	bash scripts/verify_all.sh

paper:
	bash scripts/build_paper.sh

arxiv: paper
	$(PYTHON) scripts/build_arxiv.py

checksums:
	$(PYTHON) scripts/update_checksums.py

release-candidate: verify paper
	$(PYTHON) scripts/build_release.py
	$(PYTHON) scripts/verify_release.py
