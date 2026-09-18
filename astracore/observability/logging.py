from __future__ import annotations
import json, logging, sys, time

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(record.created)),
            "level": record.levelname, "logger": record.name, "message": record.getMessage(),
        }
        if record.exc_info: payload["exception"] = self.formatException(record.exc_info)
        for key in ("guild_id", "user_id", "command", "duration_ms", "event"):
            if hasattr(record, key): payload[key] = getattr(record, key)
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

def configure(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("AstraCore")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers.clear(); logger.propagate = False
    handler = logging.StreamHandler(sys.stdout); handler.setFormatter(JsonFormatter()); logger.addHandler(handler)
    return logger
