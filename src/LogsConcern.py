import datetime


class Logs:
    LOG_PREFIX = ''

    def _log(self, msg):
        timestamp = datetime.datetime.now().isoformat()
        print(f"[{timestamp}, {self.LOG_PREFIX}] {msg}")
