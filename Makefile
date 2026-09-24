.PHONY: validate pack verify clean

validate:
	@python3 scripts/validate_submission.py submission --strict

pack:
	@./scripts/pack_submission.sh

verify:
	@./scripts/pack_submission.sh
	@./scripts/pack_submission.sh --verify-only

clean:
	rm -f submission.zip
