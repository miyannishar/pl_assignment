# Cobra Makefile

TESTS = \
  num_simple \
  bool_true \
  bool_false \
  add1_basic \
  sub1_basic \
  negate_basic \
  isnum_number \
  isnum_bool \
  isbool_bool \
  isbool_number \
  cmp_less_true \
  cmp_less_false \
  cmp_greater \
  cmp_leq \
  cmp_geq \
  cmp_equal_nums \
  cmp_equal_bools \
  if_true_branch \
  if_false_branch \
  if_nested \
  block_basic \
  loop_break \
  set_mutation \
  loop_counter \
  input_num \
  let_multi \
  let_shadow

# Runtime errors: compile to binary, run it, expect non-zero exit + "invalid argument"
ERROR_TESTS = \
  err_add_bool \
  err_equal_type_mismatch

# Compile-time errors: the compiler itself should exit non-zero (panic)
COMPILE_ERROR_TESTS = \
  err_break_outside_loop

.PRECIOUS: test/%.s

# ── Run all success tests ────────────────────────────────────────────────────
test: $(patsubst %, test/%.run, $(TESTS))
	@echo "--- Running success tests ---"
	@pass=0; fail=0; \
	for t in $(TESTS); do \
		expected=$$(cat test/$$t.expected); \
		if [ "$$t" = "input_num" ]; then \
			got=$$(./test/$$t.run 7 2>/dev/null); \
		else \
			got=$$(./test/$$t.run 2>/dev/null); \
		fi; \
		if [ "$$got" = "$$expected" ]; then \
			printf "  %-30s PASS\n" "$$t"; pass=$$((pass+1)); \
		else \
			printf "  %-30s FAIL (expected: $$expected, got: $$got)\n" "$$t"; fail=$$((fail+1)); \
		fi; \
	done; \
	echo ""; echo "Passed: $$pass  Failed: $$fail"
	@$(MAKE) test-errors

# ── Run all error tests (must exit non-zero + print "invalid argument") ───────
test-errors: $(patsubst %, test/%.run, $(ERROR_TESTS))
	@echo "--- Running error tests ---"
	@pass=0; fail=0; \
	for t in $(ERROR_TESTS); do \
		msg=$$(./test/$$t.run 2>&1); \
		code=$$?; \
		if [ $$code -ne 0 ] && echo "$$msg" | grep -q "invalid argument"; then \
			printf "  %-30s PASS\n" "$$t"; pass=$$((pass+1)); \
		else \
			printf "  %-30s FAIL (exit=$$code, msg=$$msg)\n" "$$t"; fail=$$((fail+1)); \
		fi; \
	done; \
	for t in $(COMPILE_ERROR_TESTS); do \
		cargo run -- test/$$t.snek /dev/null 2>/dev/null; \
		code=$$?; \
		if [ $$code -ne 0 ]; then \
			printf "  %-30s PASS\n" "$$t"; pass=$$((pass+1)); \
		else \
			printf "  %-30s FAIL (compiler should have rejected)\n" "$$t"; fail=$$((fail+1)); \
		fi; \
	done; \
	echo ""; echo "Error tests passed: $$pass  Failed: $$fail"

# ── Compile .snek → .s ──────────────────────────────────────────────────────
test/%.s: test/%.snek src/main.rs
	cargo run -- $< test/$*.s

# ── Assemble + link .s → .run ────────────────────────────────────────────────
test/%.run: test/%.s runtime/start.rs
	nasm -f macho64 test/$*.s -o runtime/our_code.o
	ar rcs runtime/libour_code.a runtime/our_code.o
	rustc --target x86_64-apple-darwin -L runtime/ runtime/start.rs -o test/$*.run

clean:
	rm -f test/*.s test/*.run runtime/*.o runtime/*.a
