"""Tests for internal_access.py: the Access application must stay default-deny."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(__file__))
import internal_access as ia  # noqa: E402

ENV = "INTERNAL_ACCESS_EXTRA_EMAILS"
IDP_IDS = ["idp-otp"]
CFG = {
    "hostname": "internal.blowhorn.ai",
    "app_name": "app",
    "policy_name": "pol",
    "session_duration": "24h",
    "allowed_email_domains": ["layer5.io"],
    "allowed_emails": ["lee.calcote@layer5.io"],
    "extra_emails_env": ENV,
    "allowed_idps": ["onetimepin"],
}
RAW = dict(CFG)


def fake_call(app, policy):
    def call(method, path, permission, body=None):
        if "/access/apps/" in path:
            return {"result": app}
        if "/access/policies/" in path:
            return {"result": policy}
        raise AssertionError(path)
    return call


GOOD_APP = {
    "domain": "internal.blowhorn.ai",
    "type": "self_hosted",
    "policies": [{"id": "p1"}],
    "aud": "x",
    "allowed_idps": IDP_IDS,
}
GOOD_POLICY = {
    "decision": "allow",
    "include": [
        {"email_domain": {"domain": "layer5.io"}},
        {"email": {"email": "lee.calcote@layer5.io"}},
    ],
    "exclude": [],
    "require": [],
}


class AccountTest(unittest.TestCase):
    def setUp(self):
        patch = mock.patch.dict(os.environ, {"CLOUDFLARE_ACCOUNT_ID": "acct"})
        patch.start()
        self.addCleanup(patch.stop)


class VerifyApp(AccountTest):
    def run_verify(self, app, policy, idps=IDP_IDS):
        with mock.patch.object(ia, "call", fake_call(app, policy)):
            ia.verify_app(CFG, "a1", "p1", idps)

    def test_good(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.run_verify(GOOD_APP, GOOD_POLICY)
        self.assertIn(
            "verified: one self-hosted application, default deny, allow list of 1 email domain(s) and 1 named email(s), 1 login method(s)",
            out.getvalue(),
        )

    def test_everyone_rule_rejected(self):
        bad = dict(GOOD_POLICY, include=GOOD_POLICY["include"] + [{"everyone": {}}])
        with self.assertRaises(SystemExit):
            self.run_verify(GOOD_APP, bad)

    def test_group_rule_rejected(self):
        bad = dict(GOOD_POLICY, include=GOOD_POLICY["include"] + [{"group": {"id": "g1"}}])
        with self.assertRaises(SystemExit):
            self.run_verify(GOOD_APP, bad)

    def test_rule_mixing_email_and_domain_rejected(self):
        bad = dict(GOOD_POLICY, include=[{"email": {"email": "lee.calcote@layer5.io"}, "everyone": {}}])
        with self.assertRaises(SystemExit):
            self.run_verify(GOOD_APP, bad)

    def test_bypass_rejected(self):
        with self.assertRaises(SystemExit):
            self.run_verify(GOOD_APP, dict(GOOD_POLICY, decision="bypass"))

    def test_extra_policy_rejected(self):
        with self.assertRaises(SystemExit):
            self.run_verify(dict(GOOD_APP, policies=[{"id": "p1"}, {"id": "p2"}]), GOOD_POLICY)

    def test_email_drift_rejected(self):
        bad = dict(GOOD_POLICY, include=[{"email_domain": {"domain": "layer5.io"}}, {"email": {"email": "someone@example.com"}}])
        with self.assertRaises(SystemExit):
            self.run_verify(GOOD_APP, bad)

    def test_domain_drift_rejected(self):
        bad = dict(GOOD_POLICY, include=[{"email_domain": {"domain": "example.org"}}, {"email": {"email": "lee.calcote@layer5.io"}}])
        with self.assertRaises(SystemExit):
            self.run_verify(GOOD_APP, bad)

    def test_missing_domain_rejected(self):
        bad = dict(GOOD_POLICY, include=[{"email": {"email": "lee.calcote@layer5.io"}}])
        with self.assertRaises(SystemExit):
            self.run_verify(GOOD_APP, bad)

    def test_idp_mismatch_rejected(self):
        with self.assertRaises(SystemExit):
            self.run_verify(dict(GOOD_APP, allowed_idps=["idp-other"]), GOOD_POLICY)

    def test_idp_missing_from_app_rejected(self):
        with self.assertRaises(SystemExit):
            self.run_verify(dict(GOOD_APP, allowed_idps=[]), GOOD_POLICY)

    def test_failure_message_names_no_addresses(self):
        bad = dict(GOOD_POLICY, include=[{"email": {"email": "someone@example.com"}}])
        with self.assertRaises(SystemExit) as ctx:
            self.run_verify(GOOD_APP, bad)
        self.assertNotIn("someone@example.com", str(ctx.exception))


class ResolveIdps(AccountTest):
    IDPS = [
        {"id": "id-google", "type": "google"},
        {"id": "id-otp", "type": "onetimepin"},
    ]

    def resolve(self, idps, types):
        cfg = dict(CFG, allowed_idps=types)
        with mock.patch.object(ia, "list_all", return_value=idps):
            return ia.resolve_idps(cfg)

    def test_returns_ids_in_config_order(self):
        self.assertEqual(self.resolve(self.IDPS, ["google", "onetimepin"]), ["id-google", "id-otp"])
        self.assertEqual(self.resolve(self.IDPS, ["onetimepin", "google"]), ["id-otp", "id-google"])

    def test_missing_type_exits_naming_the_type(self):
        with self.assertRaises(SystemExit) as ctx:
            self.resolve(self.IDPS[1:], ["google"])
        message = str(ctx.exception)
        self.assertIn("'google'", message)
        self.assertIn("found 0", message)
        self.assertIn("Login methods", message)

    def test_duplicate_type_exits(self):
        idps = self.IDPS + [{"id": "id-otp-2", "type": "onetimepin"}]
        with self.assertRaises(SystemExit) as ctx:
            self.resolve(idps, ["onetimepin"])
        self.assertIn("2 login methods of type 'onetimepin'", str(ctx.exception))


class AppBody(unittest.TestCase):
    def test_login_methods_listed_without_auto_redirect(self):
        body = ia.app_body(CFG, "p1", IDP_IDS)
        self.assertEqual(body["allowed_idps"], IDP_IDS)
        self.assertIs(body["auto_redirect_to_identity"], False)
        self.assertEqual(body["policies"], [{"id": "p1", "precedence": 1}])


class PolicyBody(unittest.TestCase):
    def test_domains_then_named_emails(self):
        cfg = dict(CFG, allowed_email_domains=["layer5.io"], allowed_emails=["a@example.com", "lee.calcote@layer5.io"])
        body = ia.policy_body(cfg)
        self.assertEqual(body["decision"], "allow")
        self.assertEqual(body["include"], [
            {"email_domain": {"domain": "layer5.io"}},
            {"email": {"email": "a@example.com"}},
            {"email": {"email": "lee.calcote@layer5.io"}},
        ])
        self.assertEqual(body["exclude"], [])
        self.assertEqual(body["require"], [])


class LoadConfig(unittest.TestCase):
    def write(self, **over):
        raw = dict(RAW, **over)
        dirname = tempfile.TemporaryDirectory()
        self.addCleanup(dirname.cleanup)
        path = os.path.join(dirname.name, "access.json")
        with open(path, "w") as fh:
            json.dump(raw, fh)
        return path

    def load(self, env_value=None, require=True, **over):
        # A clean environment: no extras, and no GITHUB_ACTIONS masking, unless a test sets them.
        env = {k: v for k, v in os.environ.items() if k not in (ENV, "GITHUB_ACTIONS")}
        if env_value is not None:
            env[ENV] = env_value
        with mock.patch.dict(os.environ, env, clear=True):
            return ia.load_config(self.write(**over), require_extras=require)

    def test_merges_extras_from_env(self):
        cfg = self.load("Extra.One@Example.com,\nextra.two@example.org  extra.one@example.com")
        self.assertEqual(cfg["allowed_emails"], ["extra.one@example.com", "extra.two@example.org", "lee.calcote@layer5.io"])
        self.assertEqual(cfg["allowed_email_domains"], ["layer5.io"])
        self.assertEqual(cfg["allowed_idps"], ["onetimepin"])

    def test_normalizes_and_dedupes_config(self):
        cfg = self.load(
            "a@example.com",
            allowed_email_domains=[" Layer5.IO ", "layer5.io"],
            allowed_emails=["Lee.Calcote@layer5.io"],
        )
        self.assertEqual(cfg["allowed_email_domains"], ["layer5.io"])
        self.assertEqual(cfg["allowed_emails"], ["a@example.com", "lee.calcote@layer5.io"])

    def test_malformed_extras_exit_with_count_only(self):
        with self.assertRaises(SystemExit) as ctx:
            self.load("a@example.com, not-an-email, *@example.com")
        message = str(ctx.exception)
        self.assertIn("2 malformed entries", message)
        for leaked in ("not-an-email", "*@example.com", "a@example.com"):
            self.assertNotIn(leaked, message)

    def test_ensure_exits_when_extras_unset(self):
        with self.assertRaises(SystemExit) as ctx:
            self.load(None, require=True)
        self.assertIn(ENV, str(ctx.exception))

    def test_ensure_exits_when_extras_blank(self):
        with self.assertRaises(SystemExit):
            self.load("  \n ", require=True)

    def test_check_notes_unset_extras_and_continues(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            cfg = self.load(None, require=False)
        self.assertIn("note", out.getvalue())
        self.assertEqual(cfg["allowed_emails"], ["lee.calcote@layer5.io"])

    def test_refuses_config_that_admits_nobody(self):
        with self.assertRaises(SystemExit):
            self.load(None, require=False, allowed_email_domains=[], allowed_emails=[])

    def test_extras_alone_admit_people(self):
        cfg = self.load("a@example.com", allowed_email_domains=[], allowed_emails=[])
        self.assertEqual(cfg["allowed_emails"], ["a@example.com"])

    def test_masks_every_extra_before_other_output_under_actions(self):
        out = io.StringIO()
        env = {ENV: "a@example.com b@example.org", "GITHUB_ACTIONS": "true"}
        with mock.patch.dict(os.environ, env), contextlib.redirect_stdout(out):
            ia.load_config(self.write(), require_extras=True)
        lines = out.getvalue().splitlines()
        self.assertEqual(lines[:2], ["::add-mask::a@example.com", "::add-mask::b@example.org"])
        self.assertEqual(len(lines), 2)

    def test_no_masks_outside_actions(self):
        out = io.StringIO()
        with mock.patch.dict(os.environ, {ENV: "a@example.com", "GITHUB_ACTIONS": ""}), contextlib.redirect_stdout(out):
            ia.load_config(self.write(), require_extras=True)
        self.assertEqual(out.getvalue(), "")

    def test_rejects_malformed_config_without_values(self):
        for bad in (
            {"allowed_email_domains": ["*.layer5.io"]},
            {"allowed_email_domains": ["a@layer5.io"]},
            {"allowed_emails": ["*@layer5.io"]},
            {"allowed_idps": []},
            {"allowed_idps": ["onetimepin", "onetimepin"]},
            {"extra_emails_env": "lower_case"},
        ):
            with self.subTest(bad=bad), self.assertRaises(SystemExit):
                self.load("a@example.com", **bad)

    def test_missing_key_exits(self):
        raw = dict(RAW)
        del raw["allowed_idps"]
        dirname = tempfile.TemporaryDirectory()
        self.addCleanup(dirname.cleanup)
        path = os.path.join(dirname.name, "access.json")
        with open(path, "w") as fh:
            json.dump(raw, fh)
        with self.assertRaises(SystemExit) as ctx:
            ia.load_config(path)
        self.assertIn("allowed_idps", str(ctx.exception))


class RepositoryConfig(unittest.TestCase):
    """The committed access.json is public: it may name only the team's own addresses."""

    def test_domains_look_like_domains(self):
        with open(ia.DEFAULT_CONFIG) as fh:
            raw = json.load(fh)
        self.assertTrue(raw["allowed_email_domains"])
        for d in raw["allowed_email_domains"]:
            self.assertRegex(d, ia.DOMAIN_RE.pattern)
            self.assertNotIn("@", d)
            self.assertNotIn("*", d)

    def test_emails_look_like_emails(self):
        with open(ia.DEFAULT_CONFIG) as fh:
            raw = json.load(fh)
        for e in raw["allowed_emails"]:
            self.assertRegex(e, ia.EMAIL_RE.pattern)

    def test_no_email_outside_the_allowed_domains(self):
        with open(ia.DEFAULT_CONFIG) as fh:
            raw = json.load(fh)
        domains = set(raw["allowed_email_domains"])
        for e in raw["allowed_emails"]:
            self.assertIn(e.rsplit("@", 1)[1], domains, "a named address in access.json is outside allowed_email_domains")

    def test_loads_without_extras(self):
        with mock.patch.dict(os.environ, {ENV: ""}), contextlib.redirect_stdout(io.StringIO()):
            cfg = ia.load_config(ia.DEFAULT_CONFIG, require_extras=False)
        self.assertEqual(cfg["allowed_email_domains"], ["layer5.io"])
        self.assertEqual(cfg["allowed_emails"], ["lee.calcote@layer5.io"])
        self.assertEqual(cfg["allowed_idps"], ["onetimepin"])


class MatchingApps(unittest.TestCase):
    def test_matches_host_paths_and_subdomains(self):
        apps = [
            {"id": 1, "domain": "internal.blowhorn.ai"},
            {"id": 2, "domain": "internal.blowhorn.ai/internal/finance"},
            {"id": 3, "domain": "x.internal.blowhorn.ai"},
            {"id": 4, "domain": "tells.blowhorn.ai"},
            {"id": 5, "domain": "other.example", "self_hosted_domains": ["internal.blowhorn.ai/a"]},
        ]
        self.assertEqual([a["id"] for a in ia.matching_apps(apps, "internal.blowhorn.ai")], [1, 2, 3, 5])


if __name__ == "__main__":
    unittest.main()
