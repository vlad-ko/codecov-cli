import typing
from importlib import import_module

import click

from codecov_cli.plugins.gcov import GcovPlugin
from codecov_cli.plugins.pycoverage import Pycoverage


class NoopPlugin(object):
    def run_preparation(self, collector):
        pass


def select_preparation_plugins(cli_config: typing.Dict, plugin_names: typing.List[str]):
    return [_get_plugin(cli_config, p) for p in plugin_names]


def _load_plugin_from_yaml(plugin_dict: typing.Dict):
    try:
        class_obj = import_module(plugin_dict["path"])
    except ModuleNotFoundError:
        click.secho(
            f"Unable to dynamically load plugin on path {plugin_dict['path']}",
            err=True,
        )
        return NoopPlugin()
    try:
        return class_obj(**plugin_dict["params"])
    except TypeError:
        click.secho(
            f"Unable to instantiate {class_obj} with parameters {plugin_dict['params']}",
            err=True,
        )
        return NoopPlugin()


def _get_plugin(cli_config, plugin_name):
    if plugin_name == "gcov":
        return GcovPlugin()
    if plugin_name == "pycoverage":
        return Pycoverage()
    if cli_config and plugin_name in cli_config.get("plugins", {}):
        return _load_plugin_from_yaml(cli_config["plugins"][plugin_name])
    click.secho(f"Unable to find plugin {plugin_name}", fg="magenta", err=True)
    return NoopPlugin()
