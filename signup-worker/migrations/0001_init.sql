-- Signups for coming-soon waitlists and the Blowhorn newsletter.
-- One row per (email, kind, topic). Topic is NULL for the newsletter, so
-- uniqueness needs two partial indexes: SQLite treats NULLs as distinct
-- in a plain UNIQUE constraint, and a second identical newsletter signup
-- must update the row, not add one.
CREATE TABLE IF NOT EXISTS signups (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('waitlist', 'newsletter')),
  topic TEXT,
  remark TEXT NOT NULL DEFAULT '',
  token TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL,
  unsubscribed_at TEXT,
  source_page TEXT NOT NULL DEFAULT ''
);
CREATE UNIQUE INDEX IF NOT EXISTS signups_email_kind_null_topic
  ON signups (email, kind) WHERE topic IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS signups_email_kind_topic
  ON signups (email, kind, topic) WHERE topic IS NOT NULL;

-- Per-IP rate-limit buckets, one row per IP per minute window.
CREATE TABLE IF NOT EXISTS rate_limits (
  ip TEXT NOT NULL,
  window INTEGER NOT NULL,
  count INTEGER NOT NULL,
  PRIMARY KEY (ip, window)
);
