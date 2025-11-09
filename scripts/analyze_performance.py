#!/usr/bin/env python
"""
Performance Log Analysis Script for Laser OS Tier 1

Analyzes performance logs to identify bottlenecks and trends.
"""

import re
import sys
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from statistics import mean, median, stdev

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def parse_performance_log(log_file, route_filter=None, last_n=None):
    """Parse performance log file and extract metrics."""
    
    # Pattern to match performance log entries
    # [2025-10-18 14:30:45] INFO - PERFORMANCE | Route: /dashboard | Load Time: 245ms | Queries: 8 | DB Time: 120ms | Render Time: 95ms | Total: 245ms
    pattern = r'\[(.*?)\].*?Route: (.*?) \| Load Time: (\d+)ms \| Queries: (\d+) \| DB Time: (\d+)ms \| Render Time: (\d+)ms \| Total: (\d+)ms'
    
    entries = []
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            # If last_n specified, only process last N lines
            if last_n:
                lines = lines[-last_n:]
            
            for line in lines:
                match = re.search(pattern, line)
                if match:
                    timestamp, route, load_time, queries, db_time, render_time, total_time = match.groups()
                    
                    # Filter by route if specified
                    if route_filter and route != route_filter:
                        continue
                    
                    entries.append({
                        'timestamp': datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
                        'route': route,
                        'load_time': int(load_time),
                        'queries': int(queries),
                        'db_time': int(db_time),
                        'render_time': int(render_time),
                        'total_time': int(total_time)
                    })
    
    except FileNotFoundError:
        print(f"Error: Log file not found: {log_file}")
        return []
    except Exception as e:
        print(f"Error parsing log file: {e}")
        return []
    
    return entries


def calculate_statistics(values):
    """Calculate statistics for a list of values."""
    if not values:
        return None
    
    sorted_values = sorted(values)
    
    return {
        'count': len(values),
        'min': min(values),
        'max': max(values),
        'mean': mean(values),
        'median': median(values),
        'p95': sorted_values[int(len(sorted_values) * 0.95)] if len(sorted_values) > 1 else sorted_values[0],
        'p99': sorted_values[int(len(sorted_values) * 0.99)] if len(sorted_values) > 1 else sorted_values[0],
        'stdev': stdev(values) if len(values) > 1 else 0
    }


def analyze_by_route(entries):
    """Analyze performance metrics grouped by route."""
    
    route_metrics = defaultdict(lambda: {
        'load_times': [],
        'query_counts': [],
        'db_times': [],
        'render_times': []
    })
    
    for entry in entries:
        route = entry['route']
        route_metrics[route]['load_times'].append(entry['load_time'])
        route_metrics[route]['query_counts'].append(entry['queries'])
        route_metrics[route]['db_times'].append(entry['db_time'])
        route_metrics[route]['render_times'].append(entry['render_time'])
    
    return route_metrics


def print_statistics(title, stats):
    """Print statistics in a formatted table."""
    if not stats:
        print(f"  No data available")
        return
    
    print(f"\n  {title}:")
    print(f"    Count:      {stats['count']}")
    print(f"    Min:        {stats['min']:.1f}ms")
    print(f"    Max:        {stats['max']:.1f}ms")
    print(f"    Mean:       {stats['mean']:.1f}ms")
    print(f"    Median:     {stats['median']:.1f}ms")
    print(f"    95th %ile:  {stats['p95']:.1f}ms")
    print(f"    99th %ile:  {stats['p99']:.1f}ms")
    print(f"    Std Dev:    {stats['stdev']:.1f}ms")


def print_route_analysis(route, metrics):
    """Print analysis for a specific route."""
    print(f"\n{'=' * 80}")
    print(f"Route: {route}")
    print(f"{'=' * 80}")
    
    load_time_stats = calculate_statistics(metrics['load_times'])
    query_count_stats = calculate_statistics(metrics['query_counts'])
    db_time_stats = calculate_statistics(metrics['db_times'])
    render_time_stats = calculate_statistics(metrics['render_times'])
    
    print_statistics("Load Time", load_time_stats)
    print_statistics("Query Count", query_count_stats)
    print_statistics("Database Time", db_time_stats)
    print_statistics("Render Time", render_time_stats)
    
    # Performance assessment
    print(f"\n  Performance Assessment:")
    
    if load_time_stats['mean'] < 300:
        print(f"    ✓ Load Time: Excellent (< 300ms)")
    elif load_time_stats['mean'] < 500:
        print(f"    ✓ Load Time: Good (< 500ms)")
    else:
        print(f"    ✗ Load Time: Needs Improvement (> 500ms)")
    
    if query_count_stats['mean'] < 10:
        print(f"    ✓ Query Count: Excellent (< 10 queries)")
    elif query_count_stats['mean'] < 15:
        print(f"    ✓ Query Count: Good (< 15 queries)")
    else:
        print(f"    ✗ Query Count: Needs Improvement (> 15 queries)")
    
    if db_time_stats['mean'] < 100:
        print(f"    ✓ Database Time: Excellent (< 100ms)")
    elif db_time_stats['mean'] < 200:
        print(f"    ✓ Database Time: Good (< 200ms)")
    else:
        print(f"    ✗ Database Time: Needs Improvement (> 200ms)")


def find_slowest_requests(entries, n=10):
    """Find the N slowest requests."""
    sorted_entries = sorted(entries, key=lambda x: x['total_time'], reverse=True)
    return sorted_entries[:n]


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Analyze Laser OS performance logs')
    parser.add_argument('--route', help='Filter by specific route (e.g., /dashboard)')
    parser.add_argument('--last', type=int, help='Analyze only last N log entries')
    parser.add_argument('--slowest', type=int, help='Show N slowest requests')
    parser.add_argument('--log-file', default='logs/performance.log', help='Path to performance log file')
    
    args = parser.parse_args()
    
    log_file = project_root / args.log_file
    
    print(f"\n{'=' * 80}")
    print(f"Laser OS Tier 1 - Performance Analysis")
    print(f"{'=' * 80}")
    print(f"\nLog File: {log_file}")
    
    if not log_file.exists():
        print(f"\n✗ Performance log file not found: {log_file}")
        print(f"\nPerformance logging may not be enabled yet.")
        print(f"To enable, add performance logging middleware to the application.")
        return 1
    
    # Parse log file
    entries = parse_performance_log(log_file, route_filter=args.route, last_n=args.last)
    
    if not entries:
        print(f"\n✗ No performance data found in log file")
        return 1
    
    print(f"Total Entries: {len(entries)}")
    
    if args.route:
        print(f"Filtered by Route: {args.route}")
    
    if args.last:
        print(f"Analyzing Last: {args.last} entries")
    
    # Show slowest requests if requested
    if args.slowest:
        print(f"\n{'=' * 80}")
        print(f"Top {args.slowest} Slowest Requests")
        print(f"{'=' * 80}")
        
        slowest = find_slowest_requests(entries, args.slowest)
        
        for i, entry in enumerate(slowest, 1):
            print(f"\n{i}. {entry['route']} - {entry['total_time']}ms")
            print(f"   Timestamp: {entry['timestamp']}")
            print(f"   Queries: {entry['queries']}, DB Time: {entry['db_time']}ms, Render Time: {entry['render_time']}ms")
    
    # Analyze by route
    route_metrics = analyze_by_route(entries)
    
    if args.route:
        # Single route analysis
        if args.route in route_metrics:
            print_route_analysis(args.route, route_metrics[args.route])
        else:
            print(f"\n✗ No data found for route: {args.route}")
    else:
        # All routes analysis
        print(f"\n{'=' * 80}")
        print(f"Performance Summary by Route")
        print(f"{'=' * 80}")
        
        # Sort routes by average load time (descending)
        sorted_routes = sorted(
            route_metrics.items(),
            key=lambda x: mean(x[1]['load_times']),
            reverse=True
        )
        
        for route, metrics in sorted_routes:
            print_route_analysis(route, metrics)
    
    print(f"\n{'=' * 80}")
    print(f"Analysis Complete")
    print(f"{'=' * 80}\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

