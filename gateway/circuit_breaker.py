import time

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_time=30):
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time
        self.failures = {}
        self.blocked_until = {}

    def record_failure(self, service):
        self.failures[service] = self.failures.get(service, 0) + 1
        if self.failures[service] >= self.failure_threshold:
            self.blocked_until[service] = time.time() + self.recovery_time

    def record_success(self, service):
        self.failures[service] = 0
        self.blocked_until[service] = 0

    def is_blocked(self, service):
        until = self.blocked_until.get(service, 0)
        return time.time() < until
