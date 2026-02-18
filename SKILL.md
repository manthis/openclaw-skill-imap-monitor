# openclaw-skill-imap-monitor

Generic IMAP email monitor. Polls for unread emails with optional filters, tracks state to avoid duplicate alerts.

## Usage

```bash
python3 scripts/imap-monitor.py [--dry-run] [--json]
```

## Configuration (env vars)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `IMAP_HOST` | ✅ | — | IMAP server hostname |
| `IMAP_PORT` | | `993` | Port |
| `IMAP_USER` | ✅ | — | Username/email |
| `IMAP_PASS` | ✅ | — | Password |
| `IMAP_SSL` | | `true` | Use SSL |
| `IMAP_STARTTLS` | | `false` | Use STARTTLS (when SSL=false) |
| `IMAP_FOLDER` | | `INBOX` | Mailbox folder |
| `IMAP_TIMEOUT` | | `30` | Connection timeout (seconds) |
| `FILTER_SENDER` | | — | Filter by sender |
| `FILTER_SUBJECT` | | — | Filter by subject |
| `FILTER_SINCE_DAYS` | | `1` | Only check emails from last N days |
| `IMAP_MONITOR_STATE` | | `~/.openclaw-imap-monitor-state.json` | State file |
| `IMAP_MONITOR_LOG` | | `~/logs/imap-monitor.log` | Log file |

## Dependencies

None — pure Python stdlib.

## OpenClaw Integration

```yaml
cron:
  - name: "Email Check"
    schedule: "*/15 * * * *"
    command: "python3 scripts/imap-monitor.py --json"
    env:
      IMAP_HOST: "mail.example.com"
      IMAP_USER: "user@example.com"
      IMAP_PASS: "${SECRET_IMAP_PASS}"
```
