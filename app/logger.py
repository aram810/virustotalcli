import logging
import sys
from collections.abc import Callable, Sequence
from typing import Any

import structlog
from structlog import processors, stdlib

_Processor = Callable[[Any, Any, structlog.types.EventDict], Any]


def configure_logger(debug: bool) -> None:
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    before_processors: list[_Processor] = [
        stdlib.add_logger_name,
        stdlib.add_log_level,
        processors.TimeStamper(fmt="iso"),
    ]
    after_processors: list[_Processor] = [
        processors.StackInfoRenderer(),
        processors.format_exc_info,
        processors.UnicodeDecoder(),
    ]
    common_processors: list[_Processor] = [
        *before_processors,
        *after_processors,
    ]
    all_processors: list[_Processor] = [
        stdlib.filter_by_level,
        *common_processors,
        stdlib.PositionalArgumentsFormatter(),
        stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    structlog.configure(
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
        processors=all_processors,
    )
    _configure_standard_logger(level, common_processors)


def _configure_standard_logger(
    level: str | int,
    common_processors: Sequence[Any],
) -> None:
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=common_processors,
        processor=structlog.processors.JSONRenderer(),
    )
    log_handler.setFormatter(formatter)
    logging.basicConfig(
        format="%(message)s",  # noqa: WPS323
        level=level,
        handlers=[log_handler],
    )
    root_logger = logging.getLogger()
    root_logger.handlers = [log_handler]
    root_logger.setLevel(level)
