# Diamondback Makefile

NASM := /opt/homebrew/bin/nasm

TESTS = \
  double \
  zero_arg \
  add_two \
  add_three \
  add_five \
  factorial \
  fibonacci \
  mutual_even_odd \
  mutual_countdown \
  chained_calls \
  local_vars \
  multi_locals \
  param_shadow \
  sum_to_n \
  mixed \
  if_in_fun \
  block_in_fun \
  set_in_fun \
  loop_in_fun \
  returns_bool \
  power \
  gcd \
  type_check_fun \
  expr_args \
  factorial_big \
  no_arg_in_expr

# print_test is handled separately because it has two output lines
PRINT_TESTS = print_test

.PRECIOUS: test/%.s

# ── Run all tests ─────────────────────────────────────────────────────────────
test: $(patsubst %, test/%.run, $(TESTS)) $(patsubst %, test/%.run, $(PRINT_TESTS))
	@echo "--- Running tests ---"
	@pass=0; fail=0; \
	for t in $(TESTS); do \
		expected=$$(cat test/$$t.expected); \
		got=$$(./test/$$t.run 2>/dev/null); \
		if [ "$$got" = "$$expected" ]; then \
			printf "  %-35s PASS\n" "$$t"; pass=$$((pass+1)); \
		else \
			printf "  %-35s FAIL (expected: '$$expected', got: '$$got')\n" "$$t"; fail=$$((fail+1)); \
		fi; \
	done; \
	for t in $(PRINT_TESTS); do \
		expected=$$(cat test/$$t.expected); \
		got=$$(./test/$$t.run 2>/dev/null); \
		if [ "$$got" = "$$expected" ]; then \
			printf "  %-35s PASS\n" "$$t"; pass=$$((pass+1)); \
		else \
			printf "  %-35s FAIL (expected: '$$expected', got: '$$got')\n" "$$t"; fail=$$((fail+1)); \
		fi; \
	done; \
	echo ""; echo "Passed: $$pass  Failed: $$fail"

# ── Error tests (compile-time panics) ────────────────────────────────────────
ERROR_TESTS = \
  err_undefined_fun \
  err_wrong_args \
  err_dup_param

test-errors:
	@echo "--- Running compile-error tests ---"
	@pass=0; fail=0; \
	for t in $(ERROR_TESTS); do \
		cargo run -- test/$$t.snek /dev/null 2>/dev/null; \
		code=$$?; \
		if [ $$code -ne 0 ]; then \
			printf "  %-35s PASS\n" "$$t"; pass=$$((pass+1)); \
		else \
			printf "  %-35s FAIL (compiler should have rejected)\n" "$$t"; fail=$$((fail+1)); \
		fi; \
	done; \
	echo ""; echo "Error tests passed: $$pass  Failed: $$fail"

# ── Compile .snek → .s ───────────────────────────────────────────────────────
test/%.s: test/%.snek src/main.rs
	cargo run -- $< test/$*.s

# ── Assemble + link .s → .run ─────────────────────────────────────────────────
test/%.run: test/%.s runtime/start.rs
	$(NASM) -f macho64 test/$*.s -o runtime/our_code.o
	ar rcs runtime/libour_code.a runtime/our_code.o
	rustc --target x86_64-apple-darwin -L runtime/ runtime/start.rs -o test/$*.run

clean:
	rm -f test/*.s test/*.run runtime/*.o runtime/*.a
