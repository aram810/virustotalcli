import asyncio
import functools
import pathlib
from collections.abc import Callable, Coroutine
from typing import Any

import click
import structlog

from app import handlers, logger

_logger = structlog.get_logger(__name__)


def common_options(func: Callable[..., Any]) -> Callable[..., Any]:
    decorated_func = click.option(
        "--group-max-size",
        required=False,
        default=4,
        show_default=True,
        type=click.IntRange(min=1, max=50),
    )(func)
    decorated_func = click.option("--api-key", required=True)(decorated_func)
    decorated_func = click.option(
        "--source",
        "-s",
        type=click.Path(path_type=pathlib.Path),
        required=True,
    )(decorated_func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Callable[..., Any]:
        return decorated_func(*args, **kwargs)

    return wrapper


def _run_loop_handle_exceptions(main: Coroutine[None, None, None], debug: bool) -> None:
    try:
        asyncio.run(
            main=main,
            debug=debug,
        )
    except Exception as ex:
        _logger.exception(
            "An unhandled exception occurred",
        )
        raise SystemExit(1) from ex


@click.option("--debug/--no-debug", default=False)
@click.group()
@click.pass_context
def cli(ctx: click.Context, debug: bool) -> None:
    logger.configure_logger(debug)
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug


@common_options
@cli.command()
@click.pass_context
def lookup_ips(
    ctx: click.Context, source: pathlib.Path, api_key: str, group_max_size: int
):
    _run_loop_handle_exceptions(
        main=handlers.ip_lookup_handler(source, api_key, group_max_size),
        debug=ctx.obj["debug"],
    )


@common_options
@cli.command()
@click.pass_context
def lookup_urls(
    ctx: click.Context, source: pathlib.Path, api_key: str, group_max_size: int
):
    _run_loop_handle_exceptions(
        main=handlers.url_lookup_handler(source, api_key, group_max_size),
        debug=ctx.obj["debug"],
    )


if __name__ == "__main__":
    cli()
