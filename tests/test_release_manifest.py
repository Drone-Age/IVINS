import copy
import base64
import hashlib
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
        self.next_manifest = json.loads(
            (ROOT / "manifests" / "ivins-2.0.0.0.json").read_text(encoding="utf-8")
        )

    def test_openpgp_fingerprint_ignores_ascii_armor_crc(self):
        public_key_body = b"\x04" + (b"\x00" * 20)
        packet = b"\xc6" + bytes([len(public_key_body)]) + public_key_body
        expected = hashlib.sha1(
            b"\x99" + len(public_key_body).to_bytes(2, "big") + public_key_body
        ).hexdigest().upper()
        armor = (
            "-----BEGIN PGP PUBLIC KEY BLOCK-----\n"
            "Version: regression-test\n\n"
            f"{base64.b64encode(packet).decode('ascii')}\n"
            "=ABCD\n"
            "-----END PGP PUBLIC KEY BLOCK-----\n"
        ).encode("ascii")

        self.assertEqual(MODULE.openpgp_v4_fingerprint(armor), expected)

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

    def test_schema_v2_draft_manifest_is_valid(self):
        self.assertEqual([], MODULE.validate(self.next_manifest, released=False))

    def test_schema_v2_rejects_legacy_iros_contract(self):
        self.next_manifest["components"]["iros2"]["package_namespace"] = "iros2-0"
        self.next_manifest["components"]["iros2"]["install_prefix"] = (
            "/opt/iros2_0/jazzy"
        )
        errors = MODULE.validate(self.next_manifest, released=False)
        self.assertIn("iros2.package_namespace must be iros2j", errors)
        self.assertIn("iros2.install_prefix must be /opt/iros2j", errors)

    def test_schema_v2_requires_pinned_signing_identity(self):
        key = self.next_manifest["components"]["iros2"]["apt_repository"][
            "signing_key"
        ]
        key["fingerprint"] = "unknown"
        errors = MODULE.validate(self.next_manifest, released=False)
        self.assertIn(
            "iros2 signing key fingerprint must be 40 uppercase hexadecimal characters",
            errors,
        )

    def test_schema_v2_versions_match_repository_metadata(self):
        self.next_manifest["release"]["version"] = "2.0.0.1"
        self.next_manifest["release"]["tag"] = "v2.0.0.1"
        self.next_manifest["release"]["debian_version"] = "2.0.0.1-1+deb13"
        errors = MODULE.validate(self.next_manifest, released=False)
        self.assertIn("release.version must match VERSION", errors)

    def test_schema_v2_requires_released_iros_metapackages(self):
        self.next_manifest["components"]["iros2"]["packages"] = self.next_manifest[
            "components"
        ]["iros2"]["packages"][:-1]
        errors = MODULE.validate(self.next_manifest, released=False)
        self.assertIn(
            "iros2.packages must include the required released metapackages",
            errors,
        )

    def test_schema_v2_draft_cannot_pass_released_gate(self):
        errors = MODULE.validate(self.next_manifest, released=True)
        self.assertIn("--released requires release.status=released", errors)
        self.assertIn("released manifest requires gates.hardware", errors)
        self.assertIn("released manifest requires gates.publication", errors)

    def test_historical_manifest_bytes_are_unchanged(self):
        content = (ROOT / "manifests" / "ivins-1.0.0.0.json").read_bytes()
        self.assertEqual(
            "b9d5aa11e406624ecf5f767115aa3eb0b2359cdbabb7244e80f963c54e1d0341",
            hashlib.sha256(content).hexdigest(),
        )

    def test_schema_v2_build_projection_clears_every_gate(self):
        projected = PACKAGE_MODULE.projection(self.next_manifest)
        self.assertEqual("build-input", projected["release"]["status"])
        self.assertIsNone(projected["gates"]["hardware"])
        self.assertIsNone(projected["gates"]["publication"])
        self.assertTrue(
            all(
                value is None
                for value in projected["gates"]["component_native"].values()
            )
        )

    def test_active_packaging_contract_has_no_legacy_dependency(self):
        control = (ROOT / "packaging" / "control.in").read_text(encoding="utf-8")
        installer = (ROOT / "packaging" / "install-offline.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn("Depends: @COMPONENT_DEPENDS@", control)
        self.assertNotIn("Depends: iros2-0", control)
        self.assertIn("Acquire::AllowInsecureRepositories=false", installer)
        self.assertIn("Forbidden package iros2-0 is installed.", installer)

    def test_product_activation_owns_idempotent_ogre_loader_compatibility(self):
        activation = (ROOT / "packaging" / "activate.sh").read_text(
            encoding="utf-8"
        )
        ogre = "/opt/iros2j/rviz_ogre_vendor/opt/rviz_ogre_vendor/lib/OGRE"
        self.assertIn(ogre, activation)
        self.assertLess(
            activation.index("source /opt/iros2j/setup.bash"),
            activation.index('case ":${LD_LIBRARY_PATH:-}:"'),
        )
        self.assertLess(
            activation.index('case ":${LD_LIBRARY_PATH:-}:"'),
            activation.index("source /opt/imavros/setup.bash"),
        )
        self.assertIn('IVINS_PRODUCT_VERSION="2.0.0.0"', activation)
        self.assertIn("set +u", activation)
        self.assertIn("set -u", activation)
        self.assertNotIn("/etc/ld.so.conf.d", activation)
        self.assertNotIn("patchelf", activation)

    def test_schema_v2_requires_product_activation_contract(self):
        self.next_manifest["runtime"].pop("product_activation")
        self.next_manifest["runtime"]["ogre_library_path"] = "/tmp/ogre"
        errors = MODULE.validate(self.next_manifest, released=False)
        self.assertIn(
            "runtime.product_activation must be /usr/share/ivins/activate.sh",
            errors,
        )
        self.assertIn("runtime.ogre_library_path is inconsistent", errors)

    def test_ogre_gate_requires_complete_elf_audit(self):
        gate = (ROOT / "scripts" / "run-ogre-compat-gate.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn("Plugin_OctreeZone.so.1.12.10", gate)
        self.assertIn("Plugin_PCZSceneManager.so.1.12.10", gate)
        self.assertIn("find /opt/iros2j /opt/imavros /opt/vins", gate)
        self.assertIn("test ! -s", gate)

    def test_clean_offline_gate_repeats_ogre_audit(self):
        gate = (ROOT / "scripts" / "run-clean-offline-ogre-gate.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn("sudo -n apt-get remove -y", gate)
        self.assertIn("sudo -n env DEBIAN_FRONTEND=noninteractive", gate)
        self.assertIn("run-ogre-compat-gate.sh", gate)

    def test_dataset_gate_terminates_complete_ros_process_groups(self):
        gate = (ROOT / "scripts" / "run-euroc-coverage-gate.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn("setsid ros2 launch feature_tracker", gate)
        self.assertIn("setsid ros2 launch vins_estimator", gate)
        self.assertIn('kill -INT -- "-$pgid"', gate)
        self.assertIn('kill -TERM -- "-$pgid"', gate)


if __name__ == "__main__":
    unittest.main()
