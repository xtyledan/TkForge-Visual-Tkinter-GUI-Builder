"""Regression test: redraw must restore Tk canvas item bindings."""
import unittest
from unittest.mock import MagicMock

from main import GUIDesigner


class CanvasRedrawTests(unittest.TestCase):
    def test_drag_callbacks_attached_after_widget_redraw(self):
        # Use a mocked canvas so no desktop display is required in CI.
        designer = GUIDesigner.__new__(GUIDesigner)
        designer.canvas = MagicMock()
        designer.canvas.create_rectangle.side_effect = [11, 21]
        designer.canvas.create_text.side_effect = [12, 22]

        widget = {
            "id": "label_1", "type": "label", "name": "Label",
            "x": 10, "y": 20, "width": 120, "height": 30,
            "text": "Hello", "bg": "#ffffff", "fg": "#000000",
            "font": ("Arial", 10), "canvas_id": None,
        }

        designer.draw_widget(widget)
        self.assertEqual(designer.canvas.tag_bind.call_count, 3)
        self.assertEqual(widget["canvas_id"], 11)

        widget["text"] = "Updated"
        designer.draw_widget(widget)
        self.assertEqual(widget["canvas_id"], 21)
        designer.canvas.delete.assert_called_once_with("label_1")
        self.assertEqual(designer.canvas.tag_bind.call_count, 6)
        events = [call.args[1] for call in designer.canvas.tag_bind.call_args_list]
        self.assertEqual(
            events[3:],
            ["<ButtonPress-1>", "<B1-Motion>", "<ButtonRelease-1>"]
        )
        for binding in designer.canvas.tag_bind.call_args_list[3:]:
            self.assertEqual(binding.args[0], "label_1")
            self.assertTrue(callable(binding.args[2]))


if __name__ == "__main__":
    unittest.main()
