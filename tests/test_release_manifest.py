import copy
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
PACKAGE_SPEC = importlib.util.spec_from_file_location(
    "package_manifest", ROOT / "scripts" / "package-manifest.py"
)
PACKAGE_MODULE = importlib.util.module_from_spec(PACKAGE_SPEC)
assert PACKAGE_SPEC.loader
PACKAGE_SPEC.loader.exec_module(PACKAGE_MODULE)


class ReleaseManifestTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads(
            (ROOT / "manifests" / "ivins-1.0.0.0.json").read_text(encoding="utf-8")
        )

    def test_draft_manifest_is_valid(self):
        self.assertEqual([], MODULE.validate(self.manifest, released=False))

    def test_draft_cannot_pass_released_gate(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["release"]["status"] = "draft"
        manifest["gates"]["metadata"] = None
        manifest["gates"]["component_native"]["vins"] = None
        errors = MODULE.validate(manifest, released=True)
        self.assertIn("--released requires release.status=released", errors)
        self.assertTrue(any("native gate" in error for error in errors))

    def test_malformed_component_commit_is_rejected(self):
        self.manifest["components"]["vins"]["commit"] = "not-a-sha"
        errors = MODULE.validate(self.manifest, released=False)
        self.assertIn("vins.commit must be a full Git SHA", errors)

    def test_component_repository_mismatch_is_rejected(self):
        self.manifest["components"]["vins"]["repository"] = (
            "https://github.com/example/wrong.git"
        )
        errors = MODULE.validate(self.manifest, released=False)
        self.assertIn("vins.repository is inconsistent", errors)

    def test_unapproved_component_is_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["components"]["camera"] = {
            "package": "ivins-camera-ros",
        }
        errors = MODULE.validate(manifest, released=False)
        self.assertIn(
            "components must contain exactly iros2, imavros, and vins", errors
        )

    def test_latest_component_url_is_rejected_for_release(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["release"]["status"] = "released"
        manifest["components"]["iros2"]["artifact"]["url"] = (
            "https://github.com/Drone-Age/iros2_0/releases/latest/download/"
            "iros2-0_0.1.2-1+deb13_arm64.deb"
        )
        errors = MODULE.validate(manifest, released=True)
        self.assertIn(
            "released manifest forbids a latest URL for iros2", errors
        )

    def test_build_input_projection_breaks_artifact_hash_cycle(self):
        projected = PACKAGE_MODULE.projection(self.manifest)
        self.assertEqual("build-input", projected["release"]["status"])
        self.assertIsNone(projected["artifacts"]["meta_package"]["sha256"])
        self.assertIsNone(projected["artifacts"]["offline_bundle"]["sha256"])
        self.assertIsNone(projected["gates"]["metadata"])
        self.assertTrue(
            all(
                value is None
                for value in projected["gates"]["component_native"].values()
            )
        )


if __name__ == "__main__":
    unittest.main()
