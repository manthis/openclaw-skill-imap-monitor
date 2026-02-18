#!/usr/bin/env python3
"""
imap-monitor.py — Generic IMAP email monitor for OpenClaw.
Polls IMAP server, reports unread emails with optional filters.
Pure stdlib — no external dependencies.
"""

import imaplib
import email
import email.header
import json
import os
import sys
import ssl
import socket
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path

# --- Config from env ---
IMAP_HOST = os.environ.get("IMAP_HOST", "")
IMAP_PORT = int(os.environ.get("IMAP_PORT", "993"))
IMAP_USER = os.environ.get("IMAP_USER", "")
IMAP_PASS = os.environ.get("IMAP_PASS", "")
IMAP_SSL = os.environ.get("IMAP_SSL", "true").lower() in ("true", "1", "yes")
IMAP_STARTTLS = os.environ.get("IMAP_STARTTLS", "false").lower() in ("true", "1", "yes")
IMAP_FOLDER = os.environ.get("IMAP_FOLDER", "INBOX")
IMAP_TIMEOUT = int(os.environ.get("IMAP_TIMEOUT", "30"))

# Filters
FILTER_SENDER = os.environ.get("FILTER_SENDER", "")
FILTER_SUBJECT = os.environ.get("FILTER_SUBJECT", "")
FILTER_SINCE_DAYS = int(os.environ.get("FILTER_SINCE_DAYS", "1"))

# Output
LOG_FILE = os.environ.get("IMAP_MONITOR_LOG", os.path.expanduser("~/logs/imap-monitor.log"))
STATE_FILE = os.environ.get("IMAP_MONITOR_STATE", os.path.expanduser("~/.openclaw-imap-monitor-state.json"))

# Setup logging
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
)
log = logging.getLogger(__name__)


def decode_header_value(raw):
    """Decode MIME-encoded header."""
    if raw is None:
        return ""
    parts = email.header.decode_header(raw)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return " ".join(decoded)


def load_state():
    """Load previous state (seen UIDs)."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"seen_uids": []}


def save_state(state):
    """Save state."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def connect():
    """Connect to IMAP server with timeout."""
    socket.setdefaulttimeout(IMAP_TIMEOUT)

    if IMAP_SSL:
        ctx = ssl.create_default_context()
        conn = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, ssl_context=ctx)
    else:
        conn = imaplib.IMAP4(IMAP_HOST, IMAP_PORT)
        if IMAP_STARTTLS:
            ctx = ssl.create_default_context()
            conn.starttls(ssl_context=ctx)

    conn.login(IMAP_USER, IMAP_PASS)
    return conn


def fetch_unread(conn, dry_run=False):
    """Fetch unread emails with optional filters."""
    conn.select(IMAP_FOLDER, readonly=True)

    # Build search criteria
    criteria = ["UNSEEN"]

    if FILTER_SENDER:
        criteria.append(f'FROM "{FILTER_SENDER}"')

    if FILTER_SUBJECT:
        criteria.append(f'SUBJECT "{FILTER_SUBJECT}"')

    if FILTER_SINCE_DAYS > 0:
        since_date = (datetime.now() - timedelta(days=FILTER_SINCE_DAYS)).strftime("%d-%b-%Y")
        criteria.append(f"SINCE {since_date}")

    search_str = " ".join(criteria)
    typ, data = conn.search(None, f"({search_str})")

    if typ != "OK":
        log.error(f"Search failed: {typ}")
        return []

    uids = data[0].split()
    if not uids:
        return []

    emails = []
    for uid in uids[-50:]:  # Cap at 50 most recent
        uid_str = uid.decode()
        typ, msg_data = conn.fetch(uid, "(RFC822.HEADER)")
        if typ != "OK":
            continue

        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)

        emails.append({
            "uid": uid_str,
            "from": decode_header_value(msg.get("From", "")),
            "subject": decode_header_value(msg.get("Subject", "")),
            "date": msg.get("Date", ""),
        })

    return emails


def main():
    parser = argparse.ArgumentParser(description="IMAP email monitor")
    parser.add_argument("--dry-run", action="store_true", help="Don't update state")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    if not all([IMAP_HOST, IMAP_USER, IMAP_PASS]):
        err = "Missing required env vars: IMAP_HOST, IMAP_USER, IMAP_PASS"
        log.error(err)
        print(json.dumps({"status": "error", "error": err}) if args.json else f"ERROR: {err}")
        sys.exit(1)

    try:
        conn = connect()
        all_emails = fetch_unread(conn, dry_run=args.dry_run)
        conn.logout()
    except (imaplib.IMAP4.error, socket.error, ssl.SSLError, OSError) as e:
        err = f"IMAP connection failed: {e}"
        log.error(err)
        print(json.dumps({"status": "error", "error": err}) if args.json else f"ERROR: {err}")
        sys.exit(1)

    # Filter new emails (not seen before)
    state = load_state()
    seen = set(state.get("seen_uids", []))
    new_emails = [e for e in all_emails if e["uid"] not in seen]

    # Update state
    if not args.dry_run:
        state["seen_uids"] = list(seen | {e["uid"] for e in all_emails})
        # Keep only last 500 UIDs
        state["seen_uids"] = state["seen_uids"][-500:]
        save_state(state)

    log.info(f"Found {len(all_emails)} unread, {len(new_emails)} new")

    # Output
    result = {
        "status": "ok",
        "total_unread": len(all_emails),
        "new_count": len(new_emails),
        "new_emails": new_emails,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        if new_emails:
            print(f"📧 IMAP Monitor: {len(new_emails)} new email(s)")
            for e in new_emails:
                print(f"  • From: {e['from']}")
                print(f"    Subject: {e['subject']}")
                print(f"    Date: {e['date']}")
                print()
        else:
            print(f"✅ IMAP Monitor: No new emails ({len(all_emails)} unread total)")


if __name__ == "__main__":
    main()
