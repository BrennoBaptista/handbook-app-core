import json
import logging

from platform_core.shared.logging.context import trace_id_var
from platform_core.shared.logging.formatter import JsonFormatter


def _make_record(
    message: str,
    level: int = logging.INFO,
    extra: dict[str, object] | None = None,
) -> logging.LogRecord:
    record = logging.LogRecord(
        name="platform_core.modules.auth",
        level=level,
        pathname=__file__,
        lineno=1,
        msg=message,
        args=(),
        exc_info=None,
    )
    for key, value in (extra or {}).items():
        setattr(record, key, value)
    return record


def test_format_should_include_required_fields():
    formatter = JsonFormatter(service_name="backend", environment="test")
    record = _make_record("Something happened")

    payload = json.loads(formatter.format(record))

    assert payload["level"] == "INFO"
    assert payload["service"] == "backend"
    assert payload["environment"] == "test"
    assert payload["message"] == "Something happened"
    assert "timestamp" in payload


def test_format_when_no_event_extra_should_default_to_logger_name():
    formatter = JsonFormatter(service_name="backend", environment="test")
    record = _make_record("Something happened")

    payload = json.loads(formatter.format(record))

    assert payload["event"] == "platform_core.modules.auth"


def test_format_when_event_extra_provided_should_use_it():
    formatter = JsonFormatter(service_name="backend", environment="test")
    record = _make_record("Token validated", extra={"event": "token_validated"})

    payload = json.loads(formatter.format(record))

    assert payload["event"] == "token_validated"


def test_format_when_trace_id_set_in_context_should_include_it():
    formatter = JsonFormatter(service_name="backend", environment="test")
    record = _make_record("Something happened")

    token = trace_id_var.set("trace-123")
    try:
        payload = json.loads(formatter.format(record))
    finally:
        trace_id_var.reset(token)

    assert payload["trace_id"] == "trace-123"


def test_format_when_no_trace_id_in_context_should_omit_it():
    formatter = JsonFormatter(service_name="backend", environment="test")
    record = _make_record("Something happened")

    payload = json.loads(formatter.format(record))

    assert "trace_id" not in payload


def test_format_when_optional_correlation_fields_provided_should_include_them():
    formatter = JsonFormatter(service_name="backend", environment="test")
    record = _make_record(
        "Something happened",
        extra={"user_id": "user-1", "tenant_id": "tenant-1"},
    )

    payload = json.loads(formatter.format(record))

    assert payload["user_id"] == "user-1"
    assert payload["tenant_id"] == "tenant-1"


def test_format_when_exception_info_present_should_include_it():
    formatter = JsonFormatter(service_name="backend", environment="test")
    try:
        raise ValueError("boom")
    except ValueError:
        import sys

        record = _make_record("Failed", level=logging.ERROR)
        record.exc_info = sys.exc_info()

    payload = json.loads(formatter.format(record))

    assert "ValueError: boom" in payload["exception"]
