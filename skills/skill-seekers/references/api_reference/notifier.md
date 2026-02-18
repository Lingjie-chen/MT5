# API Reference: notifier.py

**Language**: Python

**Source**: `src\skill_seekers\sync\notifier.py`

---

## Classes

### Notifier

Send notifications about sync events.

Supports:
- Webhook (HTTP POST)
- Slack (via webhook)
- Email (SMTP) - TODO
- Console (stdout)

Examples:
    notifier = Notifier()

    payload = WebhookPayload(
        event="change_detected",
        skill_name="react",
        changes=report
    )

    notifier.send(payload)

**Inherits from**: (none)

#### Methods

##### __init__(self, webhook_url: str | None = None, slack_webhook: str | None = None, email_recipients: list[str] | None = None, console: bool = True)

Initialize notifier.

Args:
    webhook_url: Webhook URL for HTTP notifications
    slack_webhook: Slack webhook URL
    email_recipients: List of email recipients
    console: Whether to print to console

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| webhook_url | str | None | None | - |
| slack_webhook | str | None | None | - |
| email_recipients | list[str] | None | None | - |
| console | bool | True | - |


##### send(self, payload: WebhookPayload)

Send notification via all configured channels.

Args:
    payload: Notification payload

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| payload | WebhookPayload | - | - |


##### _send_console(self, payload: WebhookPayload)

Print to console.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| payload | WebhookPayload | - | - |


##### _send_webhook(self, payload: WebhookPayload)

Send to generic webhook.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| payload | WebhookPayload | - | - |


##### _send_slack(self, payload: WebhookPayload)

Send to Slack via webhook.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| payload | WebhookPayload | - | - |


##### _send_email(self, payload: WebhookPayload)

Send email notification.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| payload | WebhookPayload | - | - |



