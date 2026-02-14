# API Reference: models.py

**Language**: Python

**Source**: `src\skill_seekers\sync\models.py`

---

## Classes

### ChangeType

Type of change detected.

**Inherits from**: str, Enum



### PageChange

Represents a change to a single page.

**Inherits from**: BaseModel



### ChangeReport

Report of all changes detected.

**Inherits from**: BaseModel

#### Methods

##### has_changes(self) → bool

Check if any changes were detected.

**Decorators**: `@property`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `bool`


##### change_count(self) → int

Total number of changes.

**Decorators**: `@property`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `int`




### SyncConfig

Configuration for sync monitoring.

**Inherits from**: BaseModel



### SyncState

Current state of sync monitoring.

**Inherits from**: BaseModel



### WebhookPayload

Payload for webhook notifications.

**Inherits from**: BaseModel



### Config

**Inherits from**: (none)



### Config

**Inherits from**: (none)



### Config

**Inherits from**: (none)


