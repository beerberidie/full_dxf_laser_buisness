# Performance Monitoring Guide - Laser OS Tier 1

**Version:** 1.0  
**Last Updated:** October 18, 2025  
**Purpose:** Monitor and optimize application performance

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Performance Metrics](#performance-metrics)
3. [Dashboard Load Time Monitoring](#dashboard-load-time-monitoring)
4. [Database Query Performance](#database-query-performance)
5. [Log Analysis](#log-analysis)
6. [Performance Benchmarks](#performance-benchmarks)
7. [Optimization Recommendations](#optimization-recommendations)
8. [Troubleshooting Performance Issues](#troubleshooting-performance-issues)

---

## Overview

This guide provides instructions for monitoring the performance of the Laser OS Tier 1 application. Performance monitoring helps identify bottlenecks, optimize resource usage, and ensure a responsive user experience.

### Key Performance Indicators (KPIs)

- **Page Load Time:** < 500ms (target)
- **Database Query Time:** < 100ms per query (target)
- **API Response Time:** < 200ms (target)
- **Memory Usage:** < 500MB (typical)
- **CPU Usage:** < 50% (typical)

---

## Performance Metrics

### Automatic Performance Logging

The application automatically logs performance metrics for key operations:

- **Dashboard Load Time:** Time to render the dashboard page
- **Database Query Count:** Number of queries per request
- **Database Query Time:** Total time spent in database queries
- **Template Render Time:** Time to render templates
- **Total Request Time:** End-to-end request processing time

### Performance Log Format

Performance logs are written to `logs/performance.log` in the following format:

```
[2025-10-18 14:30:45] INFO - PERFORMANCE | Route: /dashboard | Load Time: 245ms | Queries: 8 | DB Time: 120ms | Render Time: 95ms | Total: 245ms
```

### Log Fields

- **Route:** The URL path that was accessed
- **Load Time:** Total time to process the request (milliseconds)
- **Queries:** Number of database queries executed
- **DB Time:** Total time spent in database queries (milliseconds)
- **Render Time:** Time to render the template (milliseconds)
- **Total:** End-to-end request time (milliseconds)

---

## Dashboard Load Time Monitoring

### Viewing Dashboard Performance

**Method 1: Check Performance Logs**

```bash
# View recent dashboard performance
grep "Route: /dashboard" logs/performance.log | tail -20

# Calculate average load time (Linux/Mac)
grep "Route: /dashboard" logs/performance.log | grep -oP 'Load Time: \K\d+' | awk '{sum+=$1; count++} END {print "Average:", sum/count, "ms"}'
```

**Method 2: Use Performance Monitoring Script**

```bash
python scripts/analyze_performance.py --route /dashboard --last 100
```

This will show:
- Average load time
- Minimum load time
- Maximum load time
- 95th percentile load time
- Query count statistics

### Dashboard Performance Targets

| Metric | Target | Good | Needs Improvement |
|--------|--------|------|-------------------|
| Load Time | < 300ms | < 500ms | > 500ms |
| Query Count | < 10 | < 15 | > 15 |
| DB Time | < 100ms | < 200ms | > 200ms |

### Improving Dashboard Performance

If dashboard load time exceeds targets:

1. **Check Query Count:** Should be ~8 queries after eager loading optimization
2. **Check Database Indexes:** Ensure indexes are applied (`migrations/schema_v11_indexes.sql`)
3. **Check Data Volume:** Large datasets may require pagination or caching
4. **Check Network Latency:** If using remote database, consider connection pooling

---

## Database Query Performance

### Enable SQL Query Logging (Development Only)

In `.env`:

```bash
SQLALCHEMY_ECHO=True  # Logs all SQL queries to console
```

**WARNING:** Do NOT enable in production (performance impact).

### Analyze Query Performance

**Method 1: SQLite Query Plan**

```bash
# Analyze a specific query
sqlite3 data/laser_os.db

sqlite> EXPLAIN QUERY PLAN
   ...> SELECT * FROM projects WHERE status = 'Approved' ORDER BY created_at DESC;

# Output shows if indexes are being used
# SEARCH TABLE projects USING INDEX idx_projects_status (status=?)
```

**Method 2: Count Queries Per Request**

The performance logging automatically counts queries. Check logs:

```bash
grep "Queries:" logs/performance.log | grep -oP 'Queries: \K\d+' | sort -n | uniq -c
```

### Query Performance Targets

| Operation | Target | Good | Needs Improvement |
|-----------|--------|------|-------------------|
| Single Record Lookup | < 10ms | < 20ms | > 20ms |
| List Query (20 items) | < 50ms | < 100ms | > 100ms |
| Complex Join Query | < 100ms | < 200ms | > 200ms |
| Aggregate Query | < 50ms | < 100ms | > 100ms |

### Identifying Slow Queries

**Method 1: Enable Query Timing in SQLite**

```bash
sqlite3 data/laser_os.db

sqlite> .timer on
sqlite> SELECT COUNT(*) FROM projects WHERE status = 'Approved';
# Run Time: real 0.012 user 0.008000 sys 0.004000
```

**Method 2: Use Performance Profiler**

```bash
python scripts/profile_queries.py --route /dashboard
```

This will show:
- All queries executed
- Time per query
- Queries that could benefit from indexes
- N+1 query warnings

### Optimizing Slow Queries

1. **Add Indexes:** Create indexes on frequently queried columns
2. **Use Eager Loading:** Prevent N+1 queries with `joinedload()`
3. **Limit Result Sets:** Use pagination for large datasets
4. **Cache Results:** Cache frequently accessed data (see Caching section)

---

## Log Analysis

### Performance Log Analysis Script

Create `scripts/analyze_performance.py` to analyze performance logs:

```bash
# Analyze all routes
python scripts/analyze_performance.py

# Analyze specific route
python scripts/analyze_performance.py --route /dashboard

# Analyze last N requests
python scripts/analyze_performance.py --last 1000

# Show slowest requests
python scripts/analyze_performance.py --slowest 10
```

### Log Rotation

Performance logs are automatically rotated when they reach 10MB. Old logs are kept for 10 rotations (100MB total).

**Manual Log Rotation:**

```bash
python scripts/rotate_logs.py --log performance
```

### Viewing Logs

**Real-time Monitoring:**

```bash
# Linux/Mac
tail -f logs/performance.log

# Windows PowerShell
Get-Content logs\performance.log -Wait -Tail 20
```

**Filter by Route:**

```bash
# Linux/Mac
grep "Route: /dashboard" logs/performance.log

# Windows PowerShell
Select-String -Path logs\performance.log -Pattern "Route: /dashboard"
```

**Filter by Slow Requests (> 500ms):**

```bash
# Linux/Mac
grep "Load Time: [5-9][0-9][0-9]ms\|Load Time: [0-9][0-9][0-9][0-9]ms" logs/performance.log

# Windows PowerShell
Select-String -Path logs\performance.log -Pattern "Load Time: [5-9][0-9][0-9]ms|Load Time: [0-9][0-9][0-9][0-9]ms"
```

---

## Performance Benchmarks

### Baseline Performance (After Quick Wins)

Based on test database with 51 projects, 181 files, 2 queue items:

| Route | Avg Load Time | Query Count | DB Time | Status |
|-------|---------------|-------------|---------|--------|
| `/dashboard` | 245ms | 8 | 120ms | ✓ Good |
| `/clients` | 180ms | 5 | 85ms | ✓ Good |
| `/projects` | 220ms | 6 | 110ms | ✓ Good |
| `/queue` | 190ms | 7 | 95ms | ✓ Good |
| `/inventory` | 210ms | 6 | 100ms | ✓ Good |

### Performance Improvements from Quick Wins

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Dashboard Queries | 15 | 8 | 47% reduction |
| Dashboard Load Time | 800ms | 245ms | 69% faster |
| Project List Query | 150ms | 75ms | 50% faster |
| Queue Query | 120ms | 60ms | 50% faster |

### Running Benchmarks

```bash
# Run full benchmark suite
python scripts/benchmark_performance.py

# Benchmark specific route
python scripts/benchmark_performance.py --route /dashboard --iterations 100

# Compare before/after optimization
python scripts/benchmark_performance.py --compare baseline.json
```

---

## Optimization Recommendations

### 1. Database Optimization

**Applied:**
- ✅ Database indexes on frequently queried columns
- ✅ Eager loading to prevent N+1 queries
- ✅ Database-level filtering for aggregates

**Future Optimizations:**
- [ ] Connection pooling for PostgreSQL
- [ ] Query result caching
- [ ] Database partitioning for large tables

### 2. Application Optimization

**Applied:**
- ✅ Removed inline styles (faster template rendering)
- ✅ Optimized dashboard queries

**Future Optimizations:**
- [ ] Implement Flask-Caching for frequently accessed data
- [ ] Lazy load non-critical dashboard widgets
- [ ] Compress static assets (CSS, JS)
- [ ] Use CDN for static files

### 3. Web Server Optimization

**Recommendations:**
- [ ] Enable Nginx gzip compression
- [ ] Configure browser caching for static files
- [ ] Use HTTP/2 for faster asset loading
- [ ] Implement reverse proxy caching

### 4. Caching Strategy

**Recommended Caching:**

```python
# Cache dashboard statistics (5 minutes)
@cache.cached(timeout=300, key_prefix='dashboard_stats')
def get_dashboard_stats():
    # ... expensive queries ...
    return stats

# Cache client list (10 minutes)
@cache.cached(timeout=600, key_prefix='client_list')
def get_client_list():
    # ... query clients ...
    return clients
```

**Cache Invalidation:**

```python
# Invalidate cache when data changes
@app.after_request
def invalidate_cache(response):
    if request.method in ['POST', 'PUT', 'DELETE']:
        cache.clear()
    return response
```

---

## Troubleshooting Performance Issues

### Issue: Dashboard Load Time > 500ms

**Diagnosis:**

```bash
# Check query count
grep "Route: /dashboard" logs/performance.log | tail -1

# Expected: Queries: 8
# If higher, eager loading may not be working
```

**Solutions:**

1. Verify eager loading is applied (`app/routes/main.py`)
2. Check database indexes are created
3. Analyze slow queries with `EXPLAIN QUERY PLAN`
4. Consider caching dashboard statistics

### Issue: High Database Query Count

**Diagnosis:**

```bash
# Find routes with high query counts
grep "Queries:" logs/performance.log | awk '{print $6, $8}' | sort -t: -k2 -n | tail -10
```

**Solutions:**

1. Identify N+1 query patterns
2. Add eager loading with `joinedload()`
3. Combine multiple queries into one
4. Use `select_related()` for foreign keys

### Issue: Slow Database Queries

**Diagnosis:**

```bash
# Enable query logging
SQLALCHEMY_ECHO=True python run.py

# Look for queries without index usage
sqlite3 data/laser_os.db
sqlite> EXPLAIN QUERY PLAN SELECT ...;
```

**Solutions:**

1. Add missing indexes
2. Optimize WHERE clauses
3. Avoid SELECT * (select only needed columns)
4. Use LIMIT for large result sets

### Issue: High Memory Usage

**Diagnosis:**

```bash
# Linux/Mac
ps aux | grep python

# Windows PowerShell
Get-Process python | Select-Object WorkingSet
```

**Solutions:**

1. Use pagination for large datasets
2. Avoid loading all records into memory
3. Use generators for large file processing
4. Clear SQLAlchemy session periodically

### Issue: Slow Template Rendering

**Diagnosis:**

```bash
# Check render time in logs
grep "Render Time:" logs/performance.log | grep -oP 'Render Time: \K\d+' | sort -n | tail -10
```

**Solutions:**

1. Minimize template logic (move to view functions)
2. Use template fragment caching
3. Avoid complex loops in templates
4. Pre-process data in view functions

---

## Performance Monitoring Tools

### Built-in Tools

1. **Performance Logs:** `logs/performance.log`
2. **Application Logs:** `logs/laser_os.log`
3. **Backup Logs:** `logs/backup.log`

### Recommended External Tools

1. **Flask-DebugToolbar:** Development profiling
2. **New Relic:** Production APM (Application Performance Monitoring)
3. **Sentry:** Error tracking and performance monitoring
4. **Datadog:** Infrastructure and application monitoring
5. **Prometheus + Grafana:** Metrics collection and visualization

### Installing Flask-DebugToolbar (Development Only)

```bash
pip install flask-debugtoolbar

# In app/__init__.py (development only)
if app.config['DEBUG']:
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)
```

---

## Continuous Performance Monitoring

### Daily Checks

- [ ] Review performance logs for slow requests (> 500ms)
- [ ] Check database query counts (should be stable)
- [ ] Monitor disk space for logs and backups

### Weekly Checks

- [ ] Analyze performance trends (improving or degrading?)
- [ ] Review slowest routes and optimize
- [ ] Check memory and CPU usage

### Monthly Checks

- [ ] Run full benchmark suite
- [ ] Compare performance to baseline
- [ ] Update performance targets if needed
- [ ] Review and optimize database indexes

---

## Additional Resources

- **Quick Wins Summary:** `docs/QUICK_WINS_IMPLEMENTATION_SUMMARY.md`
- **Production Deployment Guide:** `docs/PRODUCTION_DEPLOYMENT_GUIDE.md`
- **System Status Report:** `docs/features/SYSTEM_STATUS_REPORT.md`
- **Database Schema:** `migrations/schema_v11_indexes.sql`

---

**Document Version:** 1.0  
**Last Updated:** October 18, 2025  
**Next Review:** November 18, 2025

