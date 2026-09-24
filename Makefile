.PHONY: pack verify clean

pack:
	@./scripts/pack_submission.sh

verify: pack
	@./scripts/pack_submission.sh --verify-only

clean:
	rm -f submission.zip
