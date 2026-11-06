"""Validation tests for imported/saved TkForge project documents."""
import unittest
from project_format import export_project, validate_project


def widget():
    return {
        "id": "button_1", "type": "button", "name": "Button",
        "x": 10, "y": 20, "width": 100, "height": 40,
        "text": "Hello", "bg": "white", "fg": "black",
        "font": ["Arial", 10], "canvas_id": 123,
        "drag_last_x": 12, "text_id": 999
    }


class ProjectValidationTests(unittest.TestCase):
    def test_valid_project_produces_independent_clean_object(self):
        original = widget()
        result = validate_project([original])
        self.assertEqual(result[0]["canvas_id"], None)
        self.assertNotIn("drag_last_x", result[0])
        self.assertEqual(result[0]["font"], ("Arial", 10))
        self.assertEqual(original["canvas_id"], 123)

    def test_export_omits_transient_canvas_state(self):
        saved = export_project([widget()])
        self.assertNotIn("canvas_id", saved[0])
        self.assertNotIn("text_id", saved[0])
        self.assertNotIn("drag_last_x", saved[0])
        self.assertEqual(validate_project(saved)[0]["id"], "button_1")

    def test_invalid_identifier_rejected(self):
        bad = widget()
        bad["id"] = 'button_1; import os'
        with self.assertRaises(ValueError):
            validate_project([bad])

    def test_type_mismatch_rejected(self):
        bad = widget()
        bad["type"] = "label"
        with self.assertRaises(ValueError):
            validate_project([bad])

    def test_duplicate_ids_rejected(self):
        with self.assertRaises(ValueError):
            validate_project([widget(), widget()])

    def test_negative_and_zero_dimensions_rejected(self):
        for invalid in (0, -1, 10001, "50", True):
            with self.subTest(value=invalid):
                bad = widget()
                bad["width"] = invalid
                with self.assertRaises(ValueError):
                    validate_project([bad])

    def test_wrong_shape_rejected(self):
        for data in (None, {}, "{}", [1]):
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    validate_project(data)

    def test_excessively_large_project_rejected(self):
        with self.assertRaises(ValueError):
            validate_project([{}] * 301)

    def test_font_validation(self):
        bad = widget()
        bad["font"] = ["Arial", "huge"]
        with self.assertRaises(ValueError):
            validate_project([bad])


if __name__ == "__main__":
    unittest.main()
