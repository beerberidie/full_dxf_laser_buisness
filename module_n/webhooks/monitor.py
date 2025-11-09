"""
Module N - Webhook Monitoring
Tracks webhook metrics, success/failure rates, and provides monitoring endpoints
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class WebhookMetric:
    """Webhook metric entry"""
    timestamp: str
    event_type: str
    ingest_id: int
    success: bool
    attempts: int
    duration_ms: float
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebhookMetric':
        """Create from dictionary"""
        return cls(**data)


class WebhookMonitor:
    """
    Webhook monitoring system.
    Tracks metrics and provides statistics.
    """
    
    def __init__(self, metrics_file: Optional[str] = None, max_metrics: int = 10000):
        """
        Initialize webhook monitor.
        
        Args:
            metrics_file: Path to metrics file (default: data/webhook_metrics.json)
            max_metrics: Maximum number of metrics to keep in memory
        """
        if metrics_file:
            self.metrics_file = Path(metrics_file)
        else:
            self.metrics_file = Path("data/webhook_metrics.json")
        
        # Ensure directory exists
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.max_metrics = max_metrics
        self.metrics: List[WebhookMetric] = []
        self._load_metrics()
    
    def _load_metrics(self):
        """Load metrics from file"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                    self.metrics = [WebhookMetric.from_dict(item) for item in data]
                logger.info(f"Loaded {len(self.metrics)} webhook metrics")
            except Exception as e:
                logger.error(f"Error loading webhook metrics: {e}")
                self.metrics = []
        else:
            self.metrics = []
    
    def _save_metrics(self):
        """Save metrics to file"""
        try:
            # Keep only the most recent metrics
            if len(self.metrics) > self.max_metrics:
                self.metrics = self.metrics[-self.max_metrics:]
            
            with open(self.metrics_file, 'w') as f:
                data = [item.to_dict() for item in self.metrics]
                json.dump(data, f, indent=2)
            logger.debug(f"Saved {len(self.metrics)} webhook metrics")
        except Exception as e:
            logger.error(f"Error saving webhook metrics: {e}")
    
    def record(
        self,
        event_type: str,
        ingest_id: int,
        success: bool,
        attempts: int,
        duration_ms: float,
        status_code: Optional[int] = None,
        error_message: Optional[str] = None
    ):
        """
        Record webhook metric.
        
        Args:
            event_type: Type of webhook event
            ingest_id: File ingest ID
            success: Whether webhook was successful
            attempts: Number of attempts made
            duration_ms: Duration in milliseconds
            status_code: HTTP status code
            error_message: Optional error message
        """
        metric = WebhookMetric(
            timestamp=datetime.utcnow().isoformat(),
            event_type=event_type,
            ingest_id=ingest_id,
            success=success,
            attempts=attempts,
            duration_ms=duration_ms,
            status_code=status_code,
            error_message=error_message
        )
        
        self.metrics.append(metric)
        self._save_metrics()
        
        logger.debug(f"Recorded webhook metric: {event_type} for file {ingest_id} (success={success})")
    
    def get_stats(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get webhook statistics for the last N hours.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Dictionary with statistics
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent_metrics = [
            m for m in self.metrics
            if datetime.fromisoformat(m.timestamp) > cutoff
        ]
        
        if not recent_metrics:
            return {
                "period_hours": hours,
                "total": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0.0,
                "avg_attempts": 0.0,
                "by_event_type": {},
                "by_status_code": {}
            }
        
        # Calculate statistics
        total = len(recent_metrics)
        successful = sum(1 for m in recent_metrics if m.success)
        failed = total - successful
        success_rate = (successful / total * 100) if total > 0 else 0.0
        avg_duration = sum(m.duration_ms for m in recent_metrics) / total
        avg_attempts = sum(m.attempts for m in recent_metrics) / total
        
        # Group by event type
        by_event_type = defaultdict(lambda: {"total": 0, "successful": 0, "failed": 0})
        for m in recent_metrics:
            by_event_type[m.event_type]["total"] += 1
            if m.success:
                by_event_type[m.event_type]["successful"] += 1
            else:
                by_event_type[m.event_type]["failed"] += 1
        
        # Group by status code
        by_status_code = defaultdict(int)
        for m in recent_metrics:
            if m.status_code:
                by_status_code[str(m.status_code)] += 1
        
        return {
            "period_hours": hours,
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": round(success_rate, 2),
            "avg_duration_ms": round(avg_duration, 2),
            "avg_attempts": round(avg_attempts, 2),
            "by_event_type": dict(by_event_type),
            "by_status_code": dict(by_status_code)
        }
    
    def get_recent_failures(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent failed webhooks.
        
        Args:
            limit: Maximum number of failures to return
            
        Returns:
            List of failed webhook metrics
        """
        failures = [m for m in reversed(self.metrics) if not m.success]
        return [m.to_dict() for m in failures[:limit]]
    
    def get_slow_webhooks(self, threshold_ms: float = 5000, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get webhooks that took longer than threshold.
        
        Args:
            threshold_ms: Duration threshold in milliseconds
            limit: Maximum number of results to return
            
        Returns:
            List of slow webhook metrics
        """
        slow = [m for m in reversed(self.metrics) if m.duration_ms > threshold_ms]
        return [m.to_dict() for m in slow[:limit]]
    
    def cleanup_old_metrics(self, max_age_days: int = 30):
        """
        Remove metrics older than max_age_days.
        
        Args:
            max_age_days: Maximum age in days
        """
        cutoff = datetime.utcnow() - timedelta(days=max_age_days)
        original_count = len(self.metrics)
        
        self.metrics = [
            m for m in self.metrics
            if datetime.fromisoformat(m.timestamp) > cutoff
        ]
        
        removed = original_count - len(self.metrics)
        if removed > 0:
            self._save_metrics()
            logger.info(f"Cleaned up {removed} old webhook metrics")
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get overall webhook health status.
        
        Returns:
            Health status dictionary
        """
        # Get stats for last hour
        stats_1h = self.get_stats(hours=1)
        stats_24h = self.get_stats(hours=24)
        
        # Determine health status
        if stats_1h["total"] == 0:
            status = "unknown"
            message = "No webhooks sent in the last hour"
        elif stats_1h["success_rate"] >= 95:
            status = "healthy"
            message = "Webhook system is operating normally"
        elif stats_1h["success_rate"] >= 80:
            status = "degraded"
            message = "Webhook success rate is below normal"
        else:
            status = "unhealthy"
            message = "Webhook system is experiencing issues"
        
        return {
            "status": status,
            "message": message,
            "last_hour": stats_1h,
            "last_24_hours": stats_24h,
            "recent_failures": self.get_recent_failures(limit=5)
        }


# Global monitor instance
_global_monitor: Optional[WebhookMonitor] = None


def get_webhook_monitor() -> WebhookMonitor:
    """Get global webhook monitor instance"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = WebhookMonitor()
    return _global_monitor

