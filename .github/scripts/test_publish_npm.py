#!/usr/bin/env python3
"""Tests for publish-npm/*.sh, the steps of publish-blowhorn-axi.yml.

Each script runs as the workflow runs it, with its inputs in the environment
and a temporary GITHUB_ENV. gh, curl, npm and sleep are stand-ins that record
their arguments; real tar, node and sha256sum check a tarball built here.

Run with `make test-scripts` (CI runs it too).
"""

import hashlib
import io
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).with_name("publish-npm")
REPO_URL = "git+https://github.com/blowhorn-ai/blowhorn-site.git"

# npm view answers from NPM_VIEW, one character per call (0 found, 1 not
# found, the last one repeating); npm publish records its arguments.
NPM = """#!/bin/sh
echo "npm $*" >> "$CALLS"
if [ "$1" = view ]; then
  n=$(cat "$NPM_COUNT" 2>/dev/null || echo 0)
  echo $((n + 1)) > "$NPM_COUNT"
  code=$(printf %s "$NPM_VIEW" | cut -c$((n + 1)))
  [ -n "$code" ] || code=$(printf %s "$NPM_VIEW" | tail -c1)
  [ "$code" = 0 ] && echo "$2"
  exit "$code"
fi
"""
# curl and gh write a copy of FIXTURE to the path after -o / -O.
FETCH = """#!/bin/sh
echo "{name} $*" >> "$CALLS"
while [ $# -gt 0 ]; do
  case "$1" in -o|-O) cp "$FIXTURE" "$2"; shift ;; esac
  shift
done
"""
SLEEP = '#!/bin/sh\necho "sleep $*" >> "$CALLS"\n'


@unittest.skipUnless(shutil.which("node") and shutil.which("tar") and shutil.which("sha256sum"),
                     "needs node, tar and sha256sum")
class PublishNpmTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        bindir = self.tmp / "bin"
        bindir.mkdir()
        stubs = {"npm": NPM, "curl": FETCH.format(name="curl"),
                 "gh": FETCH.format(name="gh"), "sleep": SLEEP}
        for name, body in stubs.items():
            (bindir / name).write_text(body)
            (bindir / name).chmod(0o755)
        self.work = self.tmp / "work"
        self.work.mkdir()
        self.calls = self.tmp / "calls"
        self.github_env = self.tmp / "github_env"
        self.github_env.touch()
        self.fixture = self.tmp / "fixture.tgz"
        self.make_tarball()
        self.env = {
            **os.environ,
            "PATH": f"{bindir}{os.pathsep}{os.environ['PATH']}",
            "CALLS": str(self.calls),
            "NPM_COUNT": str(self.tmp / "npm_count"),
            "NPM_VIEW": "1",
            "FIXTURE": str(self.fixture),
            "GITHUB_ENV": str(self.github_env),
            "GITHUB_REPOSITORY": "blowhorn-ai/blowhorn-site",
            "GH_TOKEN": "test",
            "PACKAGE": "blowhorn-axi",
            "VERSION": "0.1.0",
            "TARBALL_URL": "",
            "RELEASE_TAG": "",
            "SHA256": "",
            "DIST_TAG": "",
        }

    def make_tarball(self, name="blowhorn-axi", version="0.1.0", repo=REPO_URL):
        pkg = {"name": name, "version": version}
        if repo is not None:
            pkg["repository"] = {"type": "git", "url": repo}
        data = json.dumps(pkg).encode()
        with tarfile.open(self.fixture, "w:gz") as tar:
            info = tarfile.TarInfo("package/package.json")
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))

    def run_script(self, name, **env):
        return subprocess.run([str(SCRIPTS / name)], cwd=self.work, env={**self.env, **env},
                              capture_output=True, text=True, timeout=60)

    def calls_of(self, tool):
        lines = self.calls.read_text().splitlines() if self.calls.exists() else []
        return [line for line in lines if line.split(" ", 1)[0] == tool]

    def fetched(self, **env):
        """Run fetch.sh, then return the environment verify.sh and publish.sh see."""
        result = self.run_script("fetch.sh", **env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        line = self.github_env.read_text().splitlines()[-1]
        self.assertTrue(line.startswith("TARBALL="), line)
        return {**env, "TARBALL": line.split("=", 1)[1]}

    # fetch.sh

    def test_blowhorn_axi_defaults_to_the_v_tag(self):
        env = self.fetched()
        self.assertEqual(env["TARBALL"], "blowhorn-axi-0.1.0.tgz")
        self.assertTrue((self.work / "blowhorn-axi-0.1.0.tgz").is_file())
        self.assertEqual(self.calls_of("gh"), [
            "gh release download v0.1.0 -R blowhorn-ai/blowhorn-site"
            " -p blowhorn-axi-0.1.0.tgz -O blowhorn-axi-0.1.0.tgz"])

    def test_blowhorn_mcp_defaults_to_the_mcp_v_tag(self):
        env = self.fetched(PACKAGE="blowhorn-mcp")
        self.assertEqual(env["TARBALL"], "blowhorn-mcp-0.1.0.tgz")
        self.assertEqual(self.calls_of("gh"), [
            "gh release download mcp-v0.1.0 -R blowhorn-ai/blowhorn-site"
            " -p blowhorn-mcp-0.1.0.tgz -O blowhorn-mcp-0.1.0.tgz"])

    def test_an_explicit_release_tag_wins(self):
        self.fetched(RELEASE_TAG="axi-v0.1.0")
        self.assertIn("gh release download axi-v0.1.0 ", self.calls_of("gh")[0])

    def test_a_tarball_url_is_fetched_with_curl_over_https_only(self):
        url = "https://example.com/blowhorn-axi-0.1.0.tgz"
        self.fetched(TARBALL_URL=url)
        self.assertEqual(self.calls_of("gh"), [])
        self.assertEqual(self.calls_of("curl"), [
            "curl --fail --location --proto =https --proto-redir =https --max-time 120 -sS"
            f" -o blowhorn-axi-0.1.0.tgz {url}"])

    def test_an_unknown_package_is_refused(self):
        result = self.run_script("fetch.sh", PACKAGE="blowhorn-other")
        self.assertEqual(result.returncode, 1)
        self.assertIn("::error::package must be blowhorn-axi or blowhorn-mcp, got blowhorn-other", result.stdout)
        self.assertEqual(self.github_env.read_text(), "")

    def test_a_bad_version_is_refused(self):
        for version in ("1.2", "v1.2.3", "1.2.3; rm -rf /", "1.2.3-"):
            with self.subTest(version=version):
                result = self.run_script("fetch.sh", VERSION=version)
                self.assertEqual(result.returncode, 1)
                self.assertIn(f"::error::version must be X.Y.Z[-pre], got {version}", result.stdout)
        self.assertEqual(self.calls_of("gh") + self.calls_of("curl"), [])

    def test_a_prerelease_version_is_accepted(self):
        env = self.fetched(VERSION="0.1.0-beta.1")
        self.assertEqual(env["TARBALL"], "blowhorn-axi-0.1.0-beta.1.tgz")

    def test_a_non_https_tarball_url_is_refused(self):
        result = self.run_script("fetch.sh", TARBALL_URL="http://example.com/blowhorn-axi-0.1.0.tgz")
        self.assertEqual(result.returncode, 1)
        self.assertIn("::error::tarball_url must be HTTPS", result.stdout)
        self.assertEqual(self.calls_of("curl"), [])

    # verify.sh

    def test_the_happy_path_verifies(self):
        env = self.fetched()
        digest = hashlib.sha256(self.fixture.read_bytes()).hexdigest()
        result = self.run_script("verify.sh", SHA256=digest, **env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("blowhorn-axi-0.1.0.tgz: OK", result.stdout)
        self.assertIn("package/package.json", result.stdout)
        self.assertIn(f"{digest}  blowhorn-axi-0.1.0.tgz", result.stdout)
        self.assertEqual(self.calls_of("npm"), ["npm view blowhorn-axi@0.1.0 version"])

    def test_a_sha256_mismatch_fails(self):
        env = self.fetched()
        result = self.run_script("verify.sh", SHA256="0" * 64, **env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAILED", result.stdout)
        self.assertEqual(self.calls_of("npm"), [])

    def test_a_name_mismatch_fails(self):
        self.make_tarball(name="blowhorn-mcp")
        result = self.run_script("verify.sh", **self.fetched())
        self.assertEqual(result.returncode, 1)
        self.assertIn("::error::tarball is blowhorn-mcp, not blowhorn-axi", result.stdout)

    def test_a_version_mismatch_fails(self):
        self.make_tarball(version="0.2.0")
        result = self.run_script("verify.sh", **self.fetched())
        self.assertEqual(result.returncode, 1)
        self.assertIn("::error::tarball is version 0.2.0, input is 0.1.0", result.stdout)

    def test_a_repository_mismatch_fails(self):
        for repo in ("git+https://github.com/someone/else.git", None):
            with self.subTest(repo=repo):
                self.make_tarball(repo=repo)
                result = self.run_script("verify.sh", **self.fetched())
                self.assertEqual(result.returncode, 1)
                self.assertIn(f"::error::repository.url ({repo or ''}) must be blowhorn-ai/blowhorn-site"
                              " for provenance", result.stdout)

    def test_an_already_published_version_fails(self):
        result = self.run_script("verify.sh", NPM_VIEW="0", **self.fetched())
        self.assertEqual(result.returncode, 1)
        self.assertIn("::error::blowhorn-axi@0.1.0 is already published", result.stdout)

    # publish.sh

    def test_publish_passes_provenance_and_the_default_tag(self):
        result = self.run_script("publish.sh", **self.fetched())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls_of("npm"), [
            "npm publish ./blowhorn-axi-0.1.0.tgz --access public --provenance --tag latest"])

    def test_publish_passes_the_dist_tag(self):
        result = self.run_script("publish.sh", DIST_TAG="next", **self.fetched())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls_of("npm"), [
            "npm publish ./blowhorn-axi-0.1.0.tgz --access public --provenance --tag next"])

    # confirm.sh

    def test_confirm_succeeds_on_a_later_attempt(self):
        result = self.run_script("confirm.sh", NPM_VIEW="1110")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.calls_of("npm")), 4)
        self.assertEqual(self.calls_of("sleep"), ["sleep 10", "sleep 15", "sleep 20"])
        self.assertIn("Attempt 4 (45s elapsed): npm view blowhorn-axi@0.1.0 version", result.stdout)
        self.assertNotIn("::warning::", result.stdout)

    def test_confirm_warns_but_passes_after_the_window(self):
        result = self.run_script("confirm.sh", NPM_VIEW="1")
        self.assertEqual(result.returncode, 0, result.stderr)
        sleeps = [int(line.split()[1]) for line in self.calls_of("sleep")]
        self.assertEqual(sleeps, [10, 15, 20, 25, 30, 30, 30, 30, 30, 30, 30, 30])
        self.assertEqual(len(self.calls_of("npm")), len(sleeps) + 1)
        self.assertIn("::warning::The publish step succeeded, but the registry did not list"
                      " blowhorn-axi@0.1.0 within 310s.", result.stdout)


if __name__ == "__main__":
    unittest.main()
