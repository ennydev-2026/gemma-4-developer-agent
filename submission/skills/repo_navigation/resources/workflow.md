# TRUST-SWE navigation workflow

1. Extract exact paths, symbols, error text, APIs, and expected behavior.
2. Start with the strongest exact anchor:
   - path → `read_file`;
   - symbol/error → targeted `grep`;
   - resolved graph symbol → one graph expansion.
3. Keep at most three candidate locations and one alternative hypothesis.
4. Cross-check graph candidates with source. Downgrade graph trust when they do
   not agree or when the relevant definition cannot be represented.
5. Choose one observation that would produce different outcomes for the leading
   candidates: caller read, minimal reproduction, or targeted test.
6. After two low-information actions in one mode, change mode.
7. Edit only after one candidate has direct source or runtime evidence.
8. Re-run the same reproduction, then one focused regression test.

Do not read packages linearly. Do not keep querying a sensor after it has failed
its reliability checks.
