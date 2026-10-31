import logging


class TransportLogFilter(logging.Filter):
    """Uvicorn's WebSocket info logger includes query strings even with no-access-log."""
    def filter(self, record: logging.LogRecord) -> bool:
        if "WebSocket" in record.getMessage():
            record.msg = '{"event":"websocket_connection_activity"}'
            record.args = ()
        return True
