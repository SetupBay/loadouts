extends SceneTree
## Headless test runner: godot --headless --path . --script res://tests/run_tests.gd
## Runs every test_*() method in res://tests/test_*.gd, prints PASS/FAIL, and exits 1 on any failure.

const TEST_DIR := "res://tests"

var _failures: Array[String] = []
var _current := ""
var _errors := ErrorCatcher.new()


## Script errors (null calls, bad casts, failed asserts) only print by default: the test
## function stops, but the run still counts it as passed. This logger turns each one into a
## failure of the running test. Warnings are ignored.
class ErrorCatcher extends Logger:
	var _lock := Mutex.new()
	var _seen: Array[String] = []

	func _log_error(_function: String, file: String, line: int, code: String, rationale: String, _editor_notify: bool, error_type: int, _script_backtrace: Array[ScriptBacktrace]) -> void:
		if error_type == ERROR_TYPE_WARNING:
			return
		_lock.lock()
		_seen.append("%s (%s:%d)" % [rationale if not rationale.is_empty() else code, file.get_file(), line])
		_lock.unlock()

	func take() -> Array[String]:
		_lock.lock()
		var out := _seen.duplicate()
		_seen.clear()
		_lock.unlock()
		return out


func _initialize() -> void:
	OS.add_logger(_errors)
	_run.call_deferred()


func _run() -> void:
	var passed := 0
	var failed := 0
	for file in _test_files():
		var script: GDScript = load(TEST_DIR.path_join(file))
		if script == null or not script.can_instantiate():
			failed += 1
			print("FAIL %s: script did not load (parse error?)" % file)
			continue
		for method in script.get_script_method_list():
			var name: String = method["name"]
			if not name.begins_with("test_"):
				continue
			var suite: Object = script.new()
			suite.set("t", self)
			if suite.has_method("before_each"):
				await suite.before_each()
			_failures.clear()
			_errors.take()
			_current = "%s::%s" % [file.get_basename(), name]
			await suite.call(name)
			if suite.has_method("after_each"):
				await suite.after_each()
			for e in _errors.take():
				_failures.append("script error: " + e)
			if suite is Node and is_instance_valid(suite):
				suite.free()
			if _failures.is_empty():
				passed += 1
				print("PASS %s" % _current)
			else:
				failed += 1
				print("FAIL %s: %s" % [_current, "; ".join(_failures)])
	print("%d passed, %d failed" % [passed, failed])
	quit(1 if failed > 0 else 0)


func _test_files() -> PackedStringArray:
	var files := PackedStringArray()
	for f in DirAccess.get_files_at(TEST_DIR):
		if f.begins_with("test_") and f.ends_with(".gd"):
			files.append(f)
	files.sort()
	return files


## Assertions, called from tests as t.check(...) and t.equal(...).
func check(condition: bool, message := "expected true") -> void:
	if not condition:
		_failures.append(message)


func equal(actual: Variant, expected: Variant, message := "") -> void:
	if actual != expected:
		_failures.append("%sexpected %s, got %s" % ["" if message.is_empty() else message + ": ", var_to_str(expected), var_to_str(actual)])


## Wait for n frames of the real main loop (process and physics run headless too).
func frames(n := 1) -> void:
	for i in n:
		await process_frame
