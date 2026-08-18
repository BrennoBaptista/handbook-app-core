import logging

from platform_core.bootstrap.logging_config import configure_logging
from platform_core.shared.logging.formatter import JsonFormatter


def test_configure_logging_should_attach_json_formatter_to_root_logger():
    configure_logging(service_name="backend", environment="test")

    root_logger = logging.getLogger()

    assert len(root_logger.handlers) == 1
    assert isinstance(root_logger.handlers[0].formatter, JsonFormatter)
    assert root_logger.level == logging.INFO
