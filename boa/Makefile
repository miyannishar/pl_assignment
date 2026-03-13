# Boa Makefile

TESTS = simple add binop let_simple let_multi nested

.PRECIOUS: test/%.s

test: $(patsubst %, test/%.run, $(TESTS))
	@echo "--- Running all tests ---"
	@for t in $(TESTS); do \
		printf "%-20s => " "$$t"; \
		./test/$$t.run; \
	done

test/%.s: test/%.snek src/main.rs
	cargo run -- $< test/$*.s

test/%.run: test/%.s runtime/start.rs
	nasm -f macho64 test/$*.s -o runtime/our_code.o
	ar rcs runtime/libour_code.a runtime/our_code.o
	rustc --target x86_64-apple-darwin -L runtime/ runtime/start.rs -o test/$*.run

clean:
	rm -f test/*.s test/*.run runtime/*.o runtime/*.a
