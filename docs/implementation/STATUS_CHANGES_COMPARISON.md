# Status System Changes - Detailed Comparison

**Version:** 1.0  
**Date:** 2025-10-23

---

## 📊 Side-by-Side Comparison

### Status Values

| Current System | Proposed System | Change Type | Notes |
|----------------|-----------------|-------------|-------|
| Request | Request | ✅ KEEP | Same |
| Quote & Approval | Quote & Approval | ✅ KEEP | Same |
| Approved (POP Received) | Approved / POP Received | ✅ KEEP | Renamed slightly |
| Queued (Scheduled for Cutting) | Queued for Cutting | ✅ KEEP | Renamed slightly |
| In Progress | In Progress | ✅ KEEP | Same |
| Completed | Completed | ✅ KEEP | Same |
| Cancelled | Cancelled / On Hold | ✅ ENHANCED | Now includes "On Hold" flag |
| Quote (Legacy) | — | ❌ REMOVE | Migrate to "Quote & Approval" |
| Approved (Legacy) | — | ❌ REMOVE | Migrate to "Approved / POP Received" |

**Summary:**
- **Keep:** 6 core statuses (with minor renames)
- **Remove:** 2 legacy statuses
- **Enhance:** Cancelled status with "On Hold" capability
- **Total:** 7 statuses (6 core + 1 enhanced)

---

### Automation Triggers

| Feature | Current System | Proposed System | Change |
|---------|----------------|-----------------|--------|
| **Auto-Advance Request → Quote** | ❌ Manual only | ✅ Auto when fields valid | NEW |
| **30-Day Quote Timer** | ❌ None | ✅ Auto-start on Quote & Approval | NEW |
| **Auto-Cancel Expired Quotes** | ❌ None | ✅ Auto-cancel after 30 days | NEW |
| **25-Day Reminder** | ❌ None | ✅ Send reminder at 25 days | NEW |
| **POP → Auto-Queue** | ✅ Exists | ✅ Keep + enhance | ENHANCED |
| **Queue Status → Timestamps** | ✅ Exists | ✅ Keep | SAME |
| **Status → Activity Log** | ✅ Exists | ✅ Keep | SAME |

**Summary:**
- **New Automations:** 4
- **Enhanced Automations:** 1
- **Unchanged Automations:** 2

---

### Validation Requirements

| Status | Current Validation | Proposed Validation | Change |
|--------|-------------------|---------------------|--------|
| **Request** | None | ✅ Name, Client, Material, DXF required | NEW |
| **Quote & Approval** | None | ✅ Quote document, Quote date required | NEW |
| **Approved / POP Received** | POP document | ✅ POP document, POP date required | ENHANCED |
| **Queued for Cutting** | None | ✅ Schedule time, Queue position required | NEW |
| **In Progress** | None | ✅ Operator name, Start time required | NEW |
| **Completed** | None | ✅ Completion confirmation required | NEW |

**Summary:**
- **New Validations:** 5 statuses
- **Enhanced Validations:** 1 status
- **Total Validation Points:** 6

---

### Database Schema Changes

| Change Type | Field Name | Data Type | Purpose |
|-------------|-----------|-----------|---------|
| **ADD** | `on_hold` | BOOLEAN | Flag for on-hold status |
| **ADD** | `on_hold_reason` | TEXT | Reason for hold |
| **ADD** | `on_hold_date` | DATE | When put on hold |
| **ADD** | `quote_expiry_date` | DATE | When quote expires (30 days) |
| **ADD** | `quote_reminder_sent` | BOOLEAN | Track if reminder sent |
| **ADD** | `cancellation_reason` | TEXT | Why cancelled |
| **ADD** | `can_reinstate` | BOOLEAN | Can be reinstated |
| **UPDATE** | `status` CHECK constraint | VARCHAR(50) | Remove legacy statuses |
| **ADD** | Index on `on_hold` | INDEX | Performance |
| **ADD** | Index on `quote_expiry_date` | INDEX | Performance |
| **ADD** | Index on `can_reinstate` | INDEX | Performance |

**Summary:**
- **New Fields:** 7
- **Updated Constraints:** 1
- **New Indexes:** 3
- **Total Schema Changes:** 11

---

### Notification Events

| Event | Current System | Proposed System | Change |
|-------|----------------|-----------------|--------|
| **POP Received** | ❌ None | ✅ Email to scheduler | NEW |
| **Job Started** | ❌ None | ✅ Dashboard notification | NEW |
| **Job Completed** | ❌ None | ✅ Email to client + operator | NEW |
| **Quote Expiring (25 days)** | ❌ None | ✅ Email to client | NEW |
| **Quote Expired** | ❌ None | ✅ Email to client + admin | NEW |
| **Project Cancelled** | ❌ None | ✅ Email to admin | NEW |
| **Project On Hold** | ❌ None | ✅ Dashboard notification | NEW |
| **Project Reinstated** | ❌ None | ✅ Email to client | NEW |

**Summary:**
- **New Notifications:** 8
- **Total Notification Types:** 8

---

### User Interface Changes

| Component | Current UI | Proposed UI | Change |
|-----------|-----------|-------------|--------|
| **Status Badge** | Shows status only | Shows status + on hold + expiry | ENHANCED |
| **Action Buttons** | Basic actions | + On Hold, Reinstate buttons | NEW |
| **Project List** | Basic filters | + On Hold, Expiring Soon filters | NEW |
| **Detail Page** | Basic info | + Quote expiry countdown | NEW |
| **Modals** | None | + On Hold reason modal | NEW |
| **Alerts** | Basic | + Expiry warnings | ENHANCED |

**Summary:**
- **New UI Components:** 4
- **Enhanced Components:** 2
- **Total UI Changes:** 6

---

### API Endpoints

| Endpoint | Method | Current | Proposed | Change |
|----------|--------|---------|----------|--------|
| `/projects/<id>/status` | POST | ✅ Exists | ✅ Enhanced validation | ENHANCED |
| `/projects/<id>/toggle-hold` | POST | ❌ None | ✅ New endpoint | NEW |
| `/projects/<id>/reinstate` | POST | ❌ None | ✅ New endpoint | NEW |
| `/projects/<id>/toggle-pop` | POST | ✅ Exists | ✅ Enhanced notifications | ENHANCED |
| `/api/projects/expiring` | GET | ❌ None | ✅ New endpoint | NEW |
| `/api/projects/on-hold` | GET | ❌ None | ✅ New endpoint | NEW |

**Summary:**
- **New Endpoints:** 4
- **Enhanced Endpoints:** 2
- **Total API Changes:** 6

---

### Background Jobs

| Job | Current System | Proposed System | Schedule |
|-----|----------------|-----------------|----------|
| **Check Quote Expiry** | ❌ None | ✅ Daily at 9 AM | NEW |
| **Send Quote Reminders** | ❌ None | ✅ Daily at 10 AM | NEW |
| **Cleanup Old Data** | ❌ None | ⏳ Future enhancement | FUTURE |

**Summary:**
- **New Background Jobs:** 2
- **Scheduler Required:** ✅ APScheduler

---

### Configuration Options

| Config Key | Default Value | Purpose |
|-----------|---------------|---------|
| `AUTO_ADVANCE_TO_QUOTE` | `True` | Enable auto-advance from Request |
| `QUOTE_EXPIRY_DAYS` | `30` | Days until quote expires |
| `QUOTE_REMINDER_DAYS` | `25` | Send reminder at this day |
| `AUTO_CANCEL_EXPIRED_QUOTES` | `True` | Auto-cancel expired quotes |
| `AUTO_QUEUE_ON_POP` | `True` | Auto-queue when POP received |
| `ENABLE_EMAIL_NOTIFICATIONS` | `True` | Enable email notifications |
| `ENABLE_SMS_NOTIFICATIONS` | `False` | Enable SMS notifications |
| `ENABLE_WHATSAPP_NOTIFICATIONS` | `False` | Enable WhatsApp notifications |
| `ENABLE_BACKGROUND_SCHEDULER` | `True` | Enable background jobs |
| `QUOTE_EXPIRY_CHECK_HOUR` | `9` | Hour to check expiry (24h format) |
| `QUOTE_REMINDER_CHECK_HOUR` | `10` | Hour to send reminders (24h format) |
| `ADMIN_EMAIL` | `admin@laseros.com` | Admin notification email |
| `SCHEDULER_EMAIL` | `scheduler@laseros.com` | Scheduler notification email |

**Summary:**
- **New Config Options:** 13
- **All Optional:** ✅ Yes (defaults provided)

---

### Migration Impact

| Aspect | Impact Level | Details |
|--------|-------------|---------|
| **Database Schema** | 🔴 HIGH | 7 new fields, 3 new indexes, 1 constraint update |
| **Existing Data** | 🟡 MEDIUM | Legacy statuses need migration, no data loss |
| **Application Code** | 🔴 HIGH | New services, routes, templates |
| **User Workflow** | 🟡 MEDIUM | New features, minimal disruption |
| **Performance** | 🟢 LOW | Indexed fields, background jobs |
| **Downtime Required** | 🟢 LOW | < 5 minutes for migration |

---

### Feature Comparison Matrix

| Feature | Current | Proposed | Priority |
|---------|---------|----------|----------|
| **Auto-Advance to Quote** | ❌ | ✅ | 🔴 HIGH |
| **30-Day Quote Timer** | ❌ | ✅ | 🔴 HIGH |
| **Auto-Cancel Expired** | ❌ | ✅ | 🔴 HIGH |
| **Quote Expiry Reminder** | ❌ | ✅ | 🟡 MEDIUM |
| **On Hold Capability** | ❌ | ✅ | 🟡 MEDIUM |
| **Reinstate Workflow** | ❌ | ✅ | 🟡 MEDIUM |
| **POP Auto-Queue** | ✅ | ✅ | 🟢 LOW (exists) |
| **Email Notifications** | ❌ | ✅ | 🔴 HIGH |
| **Dashboard Alerts** | ❌ | ✅ | 🟡 MEDIUM |
| **Mobile Support** | ⏳ | ⏳ | 🟢 LOW (future) |

---

### Backward Compatibility

| Aspect | Compatible? | Migration Required? | Notes |
|--------|-------------|---------------------|-------|
| **Database Schema** | ✅ YES | ✅ YES | Add new fields with defaults |
| **Status Values** | ⚠️ PARTIAL | ✅ YES | Migrate legacy statuses |
| **API Responses** | ✅ YES | ❌ NO | New fields added, old fields kept |
| **Existing Projects** | ✅ YES | ✅ YES | Auto-migrate to new statuses |
| **Queue System** | ✅ YES | ❌ NO | No changes to queue logic |
| **Activity Logs** | ✅ YES | ❌ NO | New event types added |
| **Templates** | ✅ YES | ❌ NO | Graceful degradation |

**Summary:**
- **Breaking Changes:** 1 (legacy status removal)
- **Migration Required:** ✅ YES
- **Rollback Possible:** ✅ YES
- **Data Loss Risk:** 🟢 LOW (with proper migration)

---

### Testing Requirements

| Test Type | Current Coverage | Proposed Coverage | New Tests Required |
|-----------|-----------------|-------------------|-------------------|
| **Unit Tests** | ~60% | ~80% | +30 tests |
| **Integration Tests** | ~40% | ~70% | +20 tests |
| **E2E Tests** | ~20% | ~50% | +15 tests |
| **Performance Tests** | ❌ None | ✅ Required | +5 tests |
| **Migration Tests** | ❌ None | ✅ Required | +10 tests |

**Summary:**
- **Total New Tests:** ~80
- **Estimated Testing Time:** 2 days

---

### Documentation Updates

| Document | Current | Proposed | Update Required |
|----------|---------|----------|-----------------|
| **Status System Guide** | ✅ Exists | ✅ Update | Major update |
| **User Manual** | ✅ Exists | ✅ Update | Minor update |
| **API Documentation** | ✅ Exists | ✅ Update | Major update |
| **Database Schema** | ✅ Exists | ✅ Update | Major update |
| **Migration Guide** | ❌ None | ✅ Create | New document |
| **Automation Guide** | ❌ None | ✅ Create | New document |
| **Notification Guide** | ❌ None | ✅ Create | New document |

**Summary:**
- **Documents to Update:** 4
- **New Documents:** 3
- **Total Documentation Work:** 7 documents

---

### Risk Assessment

| Risk | Current Mitigation | Proposed Mitigation | Risk Level |
|------|-------------------|---------------------|------------|
| **Data Loss** | Database backups | + Migration testing + Rollback script | 🟢 LOW |
| **Downtime** | Maintenance window | + Quick migration + Smoke tests | 🟢 LOW |
| **User Confusion** | Basic docs | + Training + UI tooltips + Help text | 🟡 MEDIUM |
| **Email Failures** | None | + Retry logic + Queue + Monitoring | 🟡 MEDIUM |
| **Timer Failures** | None | + Error handling + Logging + Alerts | 🟡 MEDIUM |
| **Performance** | None | + Indexes + Background jobs + Caching | 🟢 LOW |

---

### Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| **Auto-Advance Rate** | 0% | > 80% | % of projects auto-advanced |
| **Quote Expiry Accuracy** | N/A | 100% | % of quotes cancelled on time |
| **Email Delivery Rate** | N/A | > 95% | % of emails successfully sent |
| **User Adoption** | N/A | > 90% | % of users using new features |
| **Support Tickets** | Baseline | < +10% | Increase in support requests |
| **Performance Impact** | Baseline | < +5% | Query response time increase |

---

### Implementation Phases

| Phase | Duration | Effort | Dependencies |
|-------|----------|--------|--------------|
| **Phase 1: Database** | 1 day | 8 hours | None |
| **Phase 2: Backend** | 1 day | 8 hours | Phase 1 |
| **Phase 3: Automation** | 2 days | 16 hours | Phase 2 |
| **Phase 4: Scheduler** | 1 day | 8 hours | Phase 3 |
| **Phase 5: Routes** | 2 days | 16 hours | Phase 2-4 |
| **Phase 6: Frontend** | 2 days | 16 hours | Phase 5 |
| **Phase 7: Notifications** | 2 days | 16 hours | Phase 3-5 |
| **Phase 8: Testing** | 2 days | 16 hours | All phases |
| **Phase 9: Documentation** | 1 day | 8 hours | All phases |

**Total:** 14 days / 112 hours

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-23  
**Status:** 📋 READY FOR REVIEW
