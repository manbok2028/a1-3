import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "api" / "diagnose.py"
SPEC = importlib.util.spec_from_file_location("diagnose_boundaries", MODULE_PATH)
diagnose = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(diagnose)


class ValidationBoundaryTests(unittest.TestCase):
    def test_validate_payload_rejects_details_over_300_characters(self):
        payload = {
            "taxType": "국세",
            "amount": "3000000",
            "period": "3개월~1년",
            "situation": "매출 감소 또는 소득 감소",
            "details": "가" * 301,
        }

        with self.assertRaises(ValueError) as context:
            diagnose.validate_payload(payload)

        self.assertIn("300", str(context.exception))

    def test_validate_payload_accepts_details_at_300_characters(self):
        payload = {
            "taxType": "지방세",
            "amount": "1",
            "period": "3개월 미만",
            "situation": "일시적인 자금 사정",
            "details": "가" * 300,
        }

        cleaned = diagnose.validate_payload(payload)
        self.assertEqual(len(cleaned["details"]), 300)
