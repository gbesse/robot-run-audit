import json
from pathlib import Path
import tempfile
import unittest

from policy_fingerprint import compare, fingerprint


FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


class PolicyFingerprintTests(unittest.TestCase):
    def test_identical_policy_in_three_languages(self):
        for locale in ("fr", "en", "es"):
            report = compare(FIXTURES / "policy-a.json", FIXTURES / "policy-a.json", locale)
            self.assertEqual(report["status"], "pass")

    def test_normalization_change_changes_identity(self):
        report = compare(FIXTURES / "policy-a.json", FIXTURES / "policy-b.json")
        self.assertEqual(report["status"], "fail")
        self.assertEqual(report["findings"][0]["component"], "normalization")

    def test_controller_change_changes_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "policy.json"
            manifest = json.loads((FIXTURES / "policy-a.json").read_text())
            manifest["files"] = {role: str(FIXTURES / name) for role, name in manifest["files"].items()}
            manifest["controller"]["units"]["joint_1"] = "deg"
            path.write_text(json.dumps(manifest))
            report = compare(FIXTURES / "policy-a.json", path)
            self.assertEqual([item["code"] for item in report["findings"]], ["controller"])

    def test_file_paths_do_not_change_fingerprint(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "policy.json"
            manifest = json.loads((FIXTURES / "policy-a.json").read_text())
            manifest["files"] = {role: str(FIXTURES / name) for role, name in manifest["files"].items()}
            path.write_text(json.dumps(manifest))
            self.assertEqual(fingerprint(path)["fingerprint"], fingerprint(FIXTURES / "policy-a.json")["fingerprint"])


if __name__ == "__main__":
    unittest.main()
