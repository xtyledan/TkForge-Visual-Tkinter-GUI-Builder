"""Headless regression tests for generated Tkinter source."""
import ast
import unittest

from main import GUIDesigner


def sample_widget(kind, suffix, text='Example'):
    return {
        "id": f"{kind}_{suffix}",
        "type": kind,
        "x": 20,
        "y": 40,
        "width": 120,
        "height": 60,
        "text": text,
        "bg": "#eeeeee",
        "fg": "#112233",
    }


class CodeGenerationTests(unittest.TestCase):
    def generate(self, widgets):
        # No display or Tk root needed for this pure code-generation method.
        designer = GUIDesigner.__new__(GUIDesigner)
        designer.widgets = widgets
        return designer._generate_tkinter_code()

    def test_empty_layout_generates_valid_python(self):
        source = self.generate([])
        ast.parse(source)
        self.assertIn("def create_gui():", source)

    def test_all_supported_widgets_generate_valid_python(self):
        kinds = (
            "button", "label", "entry", "text", "checkbutton",
            "radiobutton", "listbox", "combobox", "frame", "canvas"
        )
        source = self.generate([sample_widget(kind, i) for i, kind in enumerate(kinds)])
        ast.parse(source)
        for i, kind in enumerate(kinds):
            self.assertIn(f"{kind}_{i}.place(", source)

    def test_quotes_backslashes_and_newlines_are_escaped(self):
        value = 'She said "Hello"\nC:\\Users\\Name'
        source = self.generate([sample_widget("label", 1, value)])
        ast.parse(source)
        self.assertIn(f"text={value!r}", source)

    def test_generated_text_does_not_inject_python_statements(self):
        value = '"); __import__("os").system("echo unsafe"); #'
        source = self.generate([sample_widget("button", 1, value)])
        tree = ast.parse(source)
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
        self.assertFalse(any(
            isinstance(c.func, ast.Attribute) and c.func.attr == "system"
            for c in calls
        ))
        self.assertIn(f"text={value!r}", source)

    def test_widget_position_and_dimensions(self):
        source = self.generate([sample_widget("frame", 3)])
        ast.parse(source)
        self.assertIn("x=20", source)
        self.assertIn("y=40", source)
        self.assertIn("width=120", source)
        self.assertIn("height=60", source)


if __name__ == "__main__":
    unittest.main()
