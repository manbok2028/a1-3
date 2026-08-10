import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "api" / "diagnose.py"
SPEC = importlib.util.spec_from_file_location("diagnose", MODULE_PATH)
diagnose = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(diagnose)


class DiagnoseTests(unittest.TestCase):
    def setUp(self):
        self.payload = {"taxType": "국세", "amount": "3000000", "period": "3개월~1년", "situation": "매출 감소 또는 소득 감소", "details": ""}

    def test_validate_payload_rejects_missing_required_value(self):
        self.payload["period"] = ""
        with self.assertRaises(ValueError):
            diagnose.validate_payload(self.payload)

    def test_demo_response_has_fixed_notice_and_safe_tags(self):
        result = diagnose.demo_diagnosis(diagnose.validate_payload(self.payload))
        self.assertTrue(result["demo"])
        self.assertIn("관할 세무서", result["notice"])
        self.assertTrue(set(result["matching_tags"]).issubset(diagnose.ALLOWED_TAGS))

    def test_sanitize_answer_drops_unknown_matching_tag(self):
        result = diagnose.sanitize_answer({"summary": "요약", "possible_options": ["확인"], "next_steps": ["기관 문의"], "matching_tags": ["없는 태그", "분할 납부 검토"]})
        self.assertEqual(result["matching_tags"], ["분할 납부 검토"])
