import asyncio
import pathlib
from collections.abc import Coroutine

import click
import structlog

from app import handlers, logger

_logger = structlog.get_logger(__name__)


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


@click.option("--api-key", required=True)
@click.option(
    "--source",
    "-s",
    type=click.Path(path_type=pathlib.Path),
    required=True,
)
@cli.command()
@click.pass_context
def lookup_ips(ctx: click.Context, source: pathlib.Path, api_key: str):
    _run_loop_handle_exceptions(
        main=handlers.ip_lookup_handler(source, api_key),
        debug=ctx.obj["debug"],
    )


@click.option("--api-key", required=True)
@click.option(
    "--source",
    "-s",
    type=click.Path(path_type=pathlib.Path),
    required=True,
)
@cli.command()
@click.pass_context
def lookup_urls(ctx: click.Context, source: pathlib.Path, api_key: str):
    _run_loop_handle_exceptions(
        main=handlers.url_lookup_handler(source, api_key),
        debug=ctx.obj["debug"],
    )


if __name__ == "__main__":
    cli()
