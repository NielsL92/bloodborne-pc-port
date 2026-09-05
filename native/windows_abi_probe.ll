; Authored toolchain smoke fixture; not a lifted game routine.
target triple = "x86_64-pc-windows-msvc"
define i64 @llvm_callback_probe(i64 %a, ptr %memory, ptr %callback) {
entry:
  %v = load i64, ptr %memory, align 8
  %sum = add i64 %a, %v
  %returned = call i64 %callback(i64 %sum, ptr %memory)
  %after = load i64, ptr %memory, align 8
  %result = xor i64 %returned, %after
  ret i64 %result
}
