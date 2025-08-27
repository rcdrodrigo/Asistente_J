""Performance monitoring and metrics for the Voice Agent."""

import time
import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional
import psutil

@dataclass
class Metric:
    name: str
    value: float
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class MetricsCollector:
    def __init__(self, max_metrics: int = 1000):
        self.metrics: Dict[str, List[Metric]] = {}
        self.max_metrics = max_metrics
        self._running = False
        
    async def record(self, name: str, value: float) -> None:
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(Metric(name, value))
        if len(self.metrics[name]) > self.max_metrics:
            self.metrics[name].pop(0)
    
    def get_stats(self, name: str) -> dict:
        if not self.metrics.get(name):
            return {}
        values = [m.value for m in self.metrics[name]]
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values)
        }
    
    async def start_system_metrics(self, interval: float = 60.0) -> None:
        self._running = True
        while self._running:
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            await self.record('system.cpu', cpu)
            await self.record('system.memory', mem)
            await asyncio.sleep(interval)
    
    def stop(self) -> None:
        self._running = False

# Global instance
metrics = MetricsCollector()
