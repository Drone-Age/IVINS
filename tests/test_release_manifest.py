import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_release", ROOT / "scripts" / "validate-release.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class ReleaseManifestTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(
            (ROOT / "manifests" / "ivins-1.0.0.0.json").read_text(encoding="utf-8")
        )

    def test_draft_manifest_matches_gitlinks(self):
        self.assertEqual([], MODULE.validate(self.manifest, released=False))

    def test_draft_cannot_pass_released_gate(self):
        errors = MODULE.validate(self.manifest, released=True)
        self.assertIn("--released requires release.status=released", errors)
        self.assertTrue(any("native gate" in error for error in errors))

    def test_component_commit_mismatch_is_rejected(self):
        self.manifest["components"]["vins"]["commit"] = "0" * 40
        errors = MODULE.validate(self.manifest, released=False)
        self.assertIn(
            "vins.commit does not match the superproject gitlink", errors
        )


if __name__ == "__main__":
    unittest.main()
