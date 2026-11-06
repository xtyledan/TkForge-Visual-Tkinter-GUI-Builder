# TkForge: engineering decisions and interview notes

Use these notes only where you can explain the implementation yourself. Read the referenced source methods before discussing the project.

## Problem and user workflow

TkForge reduces the edit-run cycle for small Tkinter layouts. Users add widgets, adjust geometry and properties, preview a layout, save a JSON design, then export a standalone Python file.

## Architecture and implementation

- `main.py` contains the Tkinter editor, in-memory widget list, canvas drawing, properties controls, preview, and Python source generation.
- The widget model is a collection of dictionaries containing identifiers, types, geometry, colors, and text.
- The editor uses absolute `.place()` positioning; it is simple to export, but resizing the generated window does not rearrange widgets.
- Saving uses JSON. Generated Python is intended as a starting point for further editing, not a complete application with business logic.
- Tests in `tests/test_code_generation.py` exercise the code-generation method without creating a GUI or requiring a display.

## Specific tradeoffs

**Why Tkinter?** It is included with many desktop Python installations and suits local GUI tooling. The tradeoffs are limited native styling and an imperative UI architecture.

**Why JSON instead of SQLite?** A project is a small document. JSON is easy to inspect, share, and version. SQLite would add complexity without clear benefit until projects require search or multi-user management.

**Why absolute positioning?** It maps directly to the editor canvas. The tradeoff is poor responsiveness in the exported UI.

**Why encode labels with Python repr?** Widget text can contain quotes, newlines, and backslashes. Generating string literals with `repr` keeps such values inside the literal rather than breaking the produced Python syntax.

**Why headless tests?** They test code-generation behavior quickly in CI without relying on a graphical display; they do not prove drag-and-drop UX works.

## Failure cases and improvement opportunities

1. Validate imported JSON schemas before replacing current project state.
2. Ensure generated identifiers are valid Python names, not merely user-provided text.
3. Separate persistence, source generation, and UI logic into testable modules.
4. Add desktop integration tests under a virtual display.
5. Improve cross-platform font and color defaults.
6. Add an actual short screen recording or screenshots captured from the running application.

## Honest scope

The project is a desktop editor, not a hosted SaaS application. It has no backend, account system, database, or deployment URL. A runnable local application is the deliverable. The automated tests cover generated code syntax and common string escaping, not complete end-to-end usability.
