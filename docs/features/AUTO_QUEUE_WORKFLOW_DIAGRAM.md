# Automatic Queue Addition - Workflow Diagram

## Process Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER ACTION                                  │
│                                                                      │
│  User clicks "Toggle POP" button on project detail page             │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    TOGGLE POP FUNCTION                               │
│                                                                      │
│  1. Toggle project.pop_received = True                              │
│  2. Set project.pop_received_date = today                           │
│  3. Calculate project.pop_deadline = today + 3 days                 │
│  4. Update project.updated_at                                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    COMMIT TO DATABASE                                │
│                                                                      │
│  db.session.commit()                                                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LOG POP STATUS CHANGE                             │
│                                                                      │
│  log_pop_status_change(project.id, True, today)                     │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│              🆕 AUTO ADD TO QUEUE FUNCTION                           │
│                                                                      │
│  auto_add_to_queue(project)                                         │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
        ┌───────────────────┐  ┌──────────────────┐
        │ Check: Already    │  │ Check: Already   │
        │ in Queue?         │  │ In Progress?     │
        └─────┬─────────────┘  └────┬─────────────┘
              │                     │
              │ YES                 │ YES
              ▼                     ▼
        ┌─────────────────────────────────────┐
        │  Return: (False, "Already in...")   │
        │  Flash: Info message                │
        └─────────────────────────────────────┘
              │
              │ NO (both checks)
              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CALCULATE QUEUE POSITION                          │
│                                                                      │
│  max_position = db.session.query(                                   │
│      db.func.max(QueueItem.queue_position)                          │
│  ).scalar() or 0                                                    │
│  next_position = max_position + 1                                   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CREATE QUEUE ITEM                                 │
│                                                                      │
│  QueueItem(                                                         │
│      project_id = project.id                                        │
│      queue_position = next_position                                 │
│      status = 'Queued'                                              │
│      priority = 'Normal'                                            │
│      scheduled_date = today                                         │
│      estimated_cut_time = project.estimated_cut_time                │
│      notes = 'Automatically added...'                               │
│      added_by = 'System (Auto)'                                     │
│  )                                                                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ADD TO DATABASE SESSION                           │
│                                                                      │
│  db.session.add(queue_item)                                         │
│  db.session.flush()  # Get queue_item.id                            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LOG QUEUE ADDITION                                │
│                                                                      │
│  log_activity(                                                      │
│      entity_type='QUEUE',                                           │
│      entity_id=queue_item.id,                                       │
│      action='ADDED',                                                │
│      details='Automatically added project...',                      │
│      user='System (Auto)'                                           │
│  )                                                                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    RETURN SUCCESS                                    │
│                                                                      │
│  Return: (True, "Project automatically added...")                   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    COMMIT TO DATABASE                                │
│                                                                      │
│  db.session.commit()                                                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DISPLAY FLASH MESSAGES                            │
│                                                                      │
│  ✓ POP marked as received. Deadline: 2025-10-20                     │
│  ✓ Project automatically added to queue at position 3               │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    REDIRECT TO PROJECT DETAIL                        │
│                                                                      │
│  return redirect(url_for('projects.detail', id=id))                 │
└─────────────────────────────────────────────────────────────────────┘
```

## State Diagram

```
                    ┌──────────────────┐
                    │  Project Created │
                    │  POP: False      │
                    └────────┬─────────┘
                             │
                             │ User clicks "Toggle POP"
                             ▼
                    ┌──────────────────┐
                    │  POP Received    │
                    │  POP: True       │
                    │  Deadline: Set   │
                    └────────┬─────────┘
                             │
                             │ Automatic
                             ▼
                    ┌──────────────────┐
                    │  Added to Queue  │
                    │  Status: Queued  │
                    │  Position: N     │
                    └────────┬─────────┘
                             │
                             │ Manual or Automatic
                             ▼
                    ┌──────────────────┐
                    │  In Progress     │
                    │  Cutting Started │
                    └────────┬─────────┘
                             │
                             │
                             ▼
                    ┌──────────────────┐
                    │  Completed       │
                    │  Job Finished    │
                    └──────────────────┘
```

## Duplicate Prevention Logic

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AUTO ADD TO QUEUE                                 │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ Query Database │
                    │ for Duplicates │
                    └────────┬───────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
    ┌───────────────────────┐   ┌──────────────────────┐
    │ Status = 'Queued'?    │   │ Status = 'In Progress'│
    └───────┬───────────────┘   └──────┬───────────────┘
            │                          │
            │ Found                    │ Found
            ▼                          ▼
    ┌─────────────────────────────────────────────┐
    │  Return Failure                             │
    │  Message: "Already in queue/progress"       │
    │  Flash: Info (blue)                         │
    └─────────────────────────────────────────────┘
            │
            │ Not Found (both)
            ▼
    ┌─────────────────────────────────────────────┐
    │  Proceed with Queue Addition                │
    │  Create new QueueItem                       │
    │  Flash: Success (green)                     │
    └─────────────────────────────────────────────┘
```

## Database Transaction Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TRANSACTION START                                 │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ Update Project │
                    │ (POP fields)   │
                    └────────┬───────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ COMMIT         │
                    └────────┬───────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ Log POP Change │
                    └────────┬───────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ Create Queue   │
                    │ Item           │
                    └────────┬───────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ Log Queue Add  │
                    └────────┬───────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ COMMIT         │
                    └────────┬───────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ Success!       │
                    └────────────────┘
                             │
                             │ If Error
                             ▼
                    ┌────────────────┐
                    │ ROLLBACK       │
                    │ Flash Error    │
                    └────────────────┘
```

## User Interface Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PROJECT DETAIL PAGE                               │
│                                                                      │
│  Project: JB-2025-10-CL0001-002                                     │
│  Client: OneSourceSupply                                            │
│  Status: Approved                                                   │
│                                                                      │
│  ┌──────────────────────────────────────────────┐                  │
│  │ POP Status                                    │                  │
│  │                                               │                  │
│  │ ☐ POP Received                                │                  │
│  │ [Toggle POP] ← User clicks here               │                  │
│  └──────────────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             │ Click
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FLASH MESSAGES APPEAR                             │
│                                                                      │
│  ┌──────────────────────────────────────────────┐                  │
│  │ ✓ POP marked as received. Deadline: 2025-10-20│                  │
│  └──────────────────────────────────────────────┘                  │
│  ┌──────────────────────────────────────────────┐                  │
│  │ ✓ Project automatically added to queue at    │                  │
│  │   position 3                                  │                  │
│  └──────────────────────────────────────────────┘                  │
│                                                                      │
│  Project: JB-2025-10-CL0001-002                                     │
│  Client: OneSourceSupply                                            │
│  Status: Approved                                                   │
│                                                                      │
│  ┌──────────────────────────────────────────────┐                  │
│  │ POP Status                                    │                  │
│  │                                               │                  │
│  │ ☑ POP Received ✓                              │                  │
│  │ Received: 2025-10-17                          │                  │
│  │ Deadline: 2025-10-20                          │                  │
│  │ [Toggle POP]                                  │                  │
│  └──────────────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             │ User navigates to Queue
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    QUEUE PAGE                                        │
│                                                                      │
│  Production Queue                                                   │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Pos │ Project Code      │ Priority │ Scheduled  │ Added By   │  │
│  ├─────┼──────────────────┼──────────┼────────────┼────────────┤  │
│  │  1  │ JB-2025-10-...   │ Normal   │ 2025-10-17 │ System     │  │
│  │  2  │ JB-2025-10-...   │ Normal   │ 2025-10-17 │ System     │  │
│  │  3  │ JB-2025-10-...   │ Normal   │ 2025-10-17 │ System(Auto)│ │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  ← New project appears here automatically!                          │
└─────────────────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
                    ┌──────────────────┐
                    │  Toggle POP      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ Try Block      │
                    └────────┬───────┘
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
        ┌───────────────┐         ┌──────────────┐
        │ Success Path  │         │ Error Path   │
        └───────┬───────┘         └──────┬───────┘
                │                        │
                ▼                        ▼
        ┌───────────────┐         ┌──────────────┐
        │ Commit        │         │ Rollback     │
        │ Flash Success │         │ Flash Error  │
        └───────┬───────┘         └──────┬───────┘
                │                        │
                └────────────┬───────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ Redirect       │
                    └────────────────┘
```

## Legend

```
┌─────────┐
│ Process │  = Action or Process
└─────────┘

    │
    ▼        = Flow Direction

┌─────────┐
│ Decision│  = Decision Point
└────┬────┘
     │
  ┌──┴──┐
  ▼     ▼

✓ = Success
✗ = Failure
⚠ = Warning
ℹ = Information
```

