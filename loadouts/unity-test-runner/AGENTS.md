# AGENTS.md: Unity project with command-line tests

Unity 6 project. C# changes are checked by the Unity Test Framework, run headless. The `unity-tests` skill runs
the tests and reads the results; use it after every C# change.

## Code layout for testable C#
- Game logic in plain C# classes (no `MonoBehaviour`) in the runtime assembly, so Edit Mode tests can run it in
  milliseconds. MonoBehaviours read input, call the logic and update the scene.
- Tests in `Assets/Tests/EditMode/` and `Assets/Tests/PlayMode/`, each with its own `.asmdef`. One test class per
  class under test, named `<Class>Tests`.
- Never edit `Library/`, `Temp/`, `Logs/`, `obj/` or `UserSettings/`. Never delete or regenerate `.meta` files.

## Running tests
- The Editor binary is in `UNITY_PATH`, matching `ProjectSettings/ProjectVersion.txt`. Never run a different version.
- The project must be closed in the Editor for a command-line run. If it is open, ask the human.
- Unity exits 0 when no tests ran. A run is only green when at least one test ran and none failed.

## Done means
Edit Mode tests ran (and Play Mode tests, if you changed behaviour that needs frames), the summary shows 0 failed
and more than 0 total, no test was ignored or weakened, and you reported the command and the summary line.
