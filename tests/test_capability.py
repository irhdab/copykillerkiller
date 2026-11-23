import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "copykillerkiller" / "scripts"

_spec = importlib.util.spec_from_file_location("capability", SCRIPTS / "capability.py")
assert _spec is not None and _spec.loader is not None
capability = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(capability)


def run_capability(*args, env=None):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "capability.py"), *args],
        capture_output=True, encoding="utf-8", env=env,
    )


class CapabilityProbeTest(unittest.TestCase):
    def test_cli_returns_a_declared_tier(self):
        result = run_capability()
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["schema_version"], 1)
        self.assertIn(data["tier"], capability.TIERS)
        self.assertEqual(
            sorted(data["checks"]), ["pdftotext", "python", "temp_write"]
        )
        self.assertTrue(data["checks"]["python"]["ok"])

    def test_tier_only_prints_one_token(self):
        result = run_capability("--tier-only")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(result.stdout.strip(), capability.TIERS)
        self.assertEqual(len(result.stdout.strip().split()), 1)

    def test_missing_pdftotext_lowers_tier_to_reduced(self):
        env = dict(os.environ, PATH="")
        result = run_capability(env=env)
        data = json.loads(result.stdout)
        self.assertFalse(data["checks"]["pdftotext"]["ok"])
        self.assertEqual(data["tier"], "reduced")
        self.assertIn("txt", data["next_step"])

    def test_manual_path_wins_over_reduced(self):
        with mock.patch.object(
            capability, "check_pdftotext",
            return_value={"ok": False, "path": None, "version": None},
        ), mock.patch.object(
            capability, "check_temp_write",
            return_value={"ok": False, "dir": None, "error": "PermissionError"},
        ):
            data = capability.assess()
        self.assertEqual(data["tier"], "manual")
        self.assertFalse(data["docx_comment_copy"])

    def test_full_tier_requires_every_check(self):
        with mock.patch.object(
            capability, "check_pdftotext",
            return_value={"ok": True, "path": "/usr/bin/pdftotext", "version": "24.02"},
        ), mock.patch.object(
            capability, "check_temp_write",
            return_value={"ok": True, "dir": "/tmp", "error": None},
        ):
            data = capability.assess()
        self.assertEqual(data["tier"], "full")
        self.assertTrue(data["docx_comment_copy"])


class InstallShTest(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.skills = self.root / "skills"
        self.install = REPO / "install.sh"

    def run_install(self, *args):
        return subprocess.run(
            ["sh", str(self.install), *map(str, args)],
            capture_output=True, encoding="utf-8", cwd=self.root,
        )

    def test_installs_skill_folder_and_reports_tier(self):
        result = self.run_install("--dir", self.skills)
        self.assertEqual(result.returncode, 0, result.stderr)
        target = self.skills / "copykillerkiller"
        self.assertTrue((target / "SKILL.md").is_file())
        self.assertTrue((target / "references" / "capabilities.md").is_file())
        self.assertTrue((target / "scripts" / "capability.py").is_file())
        self.assertIn("capability tier:", result.stdout)

    def test_existing_install_is_not_replaced_without_force(self):
        self.assertEqual(self.run_install("--dir", self.skills).returncode, 0)
        marker = self.skills / "copykillerkiller" / "SKILL.md"
        before = marker.read_text(encoding="utf-8")
        again = self.run_install("--dir", self.skills)
        self.assertNotEqual(again.returncode, 0)
        self.assertEqual(marker.read_text(encoding="utf-8"), before)

    def test_force_moves_previous_install_to_a_backup(self):
        self.assertEqual(self.run_install("--dir", self.skills).returncode, 0)
        forced = self.run_install("--dir", self.skills, "--force")
        self.assertEqual(forced.returncode, 0, forced.stderr)
        backups = list(self.skills.glob("copykillerkiller.bak.*"))
        self.assertEqual(len(backups), 1)
        self.assertTrue((backups[0] / "SKILL.md").is_file())

    def test_list_prints_every_supported_agent(self):
        result = self.run_install("--list")
        self.assertEqual(result.returncode, 0, result.stderr)
        for agent in ("codex", "claude", "hermes", "cursor", "project"):
            self.assertIn(agent, result.stdout)

    def test_installed_copy_runs_its_probe_from_the_new_location(self):
        self.assertEqual(self.run_install("--dir", self.skills).returncode, 0)
        probe = self.skills / "copykillerkiller" / "scripts" / "capability.py"
        result = subprocess.run(
            [sys.executable, str(probe), "--tier-only"],
            capture_output=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(result.stdout.strip(), capability.TIERS)


if __name__ == "__main__":
    unittest.main()
