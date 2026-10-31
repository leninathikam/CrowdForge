import logging
from apps.server.logging_utils import TransportLogFilter


def test_websocket_query_credentials_are_not_logged():
    record = logging.LogRecord("uvicorn.error", logging.INFO, "", 0, '%s - "WebSocket %s" [accepted]', ("client", "/ws?token=sensitive-value"), None)
    assert TransportLogFilter().filter(record)
    assert "sensitive-value" not in record.getMessage()
