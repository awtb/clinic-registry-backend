from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import Histogram


http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ("method", "route", "status_class"),
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ("method", "route", "status_class"),
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "In-progress HTTP requests",
    ("method", "route"),
)
