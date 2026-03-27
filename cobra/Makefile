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

ERROR_TESTS = \
  err_add_bool \
  err_equal_type_mismatch \
  err_break_outside_loop

.PRECIOUS: test/%.s

# ── Run all success tests ────────────────────────────────────────────────────
test: $(patsubst %, test/%.run, $(TESTS))
	@echo "--- Running success tests ---"
	@pass=0; fail=0; \
	for t in $(TESTS); do \
		expected=$$(cat test/$$t.expected); \
		got=$$(./test/$$t.run 2>/dev/null); \
		if [ "$$got" = "$$expected" ]; then \
			printf "  %-30s PASS\n" "$$t"; pass=$$((pass+1)); \
		else \
			printf "  %-30s FAIL (expected: $$expected, got: $$got)\n" "$$t"; fail=$$((fail+1)); \
		fi; \
	done; \
	echo ""; echo "Passed: $$pass  Failed: $$fail"

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
