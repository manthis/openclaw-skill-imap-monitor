# 📧 openclaw-skill-imap-monitor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://github.com/OpenAgentsInc/openclaw)

Generic IMAP email monitor for OpenClaw. Zero dependencies — pure Python stdlib.

## Quick Start

```bash
git clone https://github.com/manthis/openclaw-skill-imap-monitor.git
cd openclaw-skill-imap-monitor

# Configure
export IMAP_HOST="mail.example.com"
export IMAP_PORT=993
export IMAP_USER="user@example.com"
export IMAP_PASS="your-password-here"

# Run
python3 scripts/imap-monitor.py

# Dry run
python3 scripts/imap-monitor.py --dry-run --json
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `IMAP_HOST` | — | IMAP server hostname |
| `IMAP_PORT` | `993` | Port number |
| `IMAP_USER` | — | Username/email |
| `IMAP_PASS` | — | Password |
| `IMAP_SSL` | `true` | Use SSL connection |
| `IMAP_STARTTLS` | `false` | Use STARTTLS |
| `IMAP_FOLDER` | `INBOX` | Mailbox to monitor |
| `FILTER_SENDER` | — | Filter by sender address |
| `FILTER_SUBJECT` | — | Filter by subject keyword |
| `FILTER_SINCE_DAYS` | `1` | Look back N days |

> ⚠️ **Security:** Never store passwords in config files. Use environment variables or a secrets manager.

## Features

- 🔒 SSL/STARTTLS support
- ⏱️ Native Python timeout (no external `timeout` command)
- 🔍 Sender/subject/date filters
- 📊 State tracking — only alerts on new emails
- 📋 JSON output for automation
- 🐍 Zero dependencies — Python stdlib only

## Requirements

- Python 3.8+

## License

MIT
