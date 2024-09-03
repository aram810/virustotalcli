import functools
import pathlib
from collections.abc import Callable
from typing import Any

import click
import structlog

from app import handlers, logger

_logger = structlog.get_logger(__name__)

_JSON_FILE = "json-file"


def _source_validator(
    ctx: click.Context, param: click.Parameter, value: pathlib.Path | None
) -> pathlib.Path | None:
    if ctx.params["reader"] == _JSON_FILE and not value:
        raise click.BadParameter(
            "{0} is required when reader is {1}".format(param.name, _JSON_FILE),
            ctx=ctx,
            param=param,
        )

    return value


def _common_options(func: Callable[..., Any]) -> Callable[..., Any]:
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
        required=False,
        callback=_source_validator,
    )(decorated_func)
    decorated_func = click.option(
        "--reader",
        "-r",
        type=click.Choice([_JSON_FILE, "cli"]),
        default="json-file",
        show_default=True,
        required=False,
        is_eager=True,
    )(decorated_func)
    decorated_func = click.option(
        "--presenter",
        "-p",
        type=click.Choice([_JSON_FILE, "cli"]),
        default="json-file",
        show_default=True,
        required=False,
    )(decorated_func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Callable[..., Any]:
        return decorated_func(*args, **kwargs)

    return wrapper


@click.option("--debug/--no-debug", default=False)
@click.group()
@click.pass_context
def cli(ctx: click.Context, debug: bool) -> None:
    logger.configure_logger(debug)
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug


@_common_options
@cli.command()
@click.pass_context
def lookup_ips(
    ctx: click.Context,
    api_key: str,
    group_max_size: int,
    reader: str,
    presenter: str,
    source: pathlib.Path | None = None,
) -> None:
    handlers.run_loop_handle_exceptions(
        main=handlers.ip_lookup_handler(
            source=source,
            api_key=api_key,
            group_max_size=group_max_size,
            reader=reader,
            presenter=presenter,
        ),
        debug=ctx.obj["debug"],
    )


@_common_options
@cli.command()
@click.pass_context
def lookup_urls(
    ctx: click.Context,
    api_key: str,
    group_max_size: int,
    reader: str,
    presenter: str,
    source: pathlib.Path | None = None,
) -> None:
    handlers.run_loop_handle_exceptions(
        main=handlers.url_lookup_handler(
            source=source,
            api_key=api_key,
            group_max_size=group_max_size,
            reader=reader,
            presenter=presenter,
        ),
        debug=ctx.obj["debug"],
    )


if __name__ == "__main__":
    cli()
