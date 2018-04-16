#!/usr/bin/env python2
"""
Main executable for the master thesis code.
"""
import pkgutil

import click

import experiments

from network.network import Network
from attestation.database import MultiChainDB

def list_experiments():
    """
    Returns the availeable experiments which are found in the 'experiments'
    directory.
    """
    result = []
    package = experiments
    for _, modname, _ in pkgutil.iter_modules(package.__path__):
        result.append(modname)
    return result

def load_experiment(experiment):
    """
    Returns a module instance of the selected experiment.
    """
    package = experiments
    path = package.__name__ + '.' + experiment
    module = __import__(path, globals(), locals(), fromlist="dummy")
    return module

def run_experiment(experiment):
    """
    Runs an experiment.
    """
    assert isinstance(experiment, experiments.base_experiment.BaseExperiment)

    experiment._preprocessing()
    experiment._run()
    experiment._visualize()

@click.group()
@click.option('--db', default="databases/multichain_10000.db")
@click.pass_context
def main(ctx, db):
    """
    Main function.
    """
    ctx.obj['DB'] = db

@main.command()
@click.argument('experiment',
                type=click.Choice(list_experiments()),
                default="simple")
@click.pass_context
def experiment(ctx, experiment):
    """
    Experiment command.
    """
    exp = load_experiment(experiment)
    run_experiment(exp.Experiment(ctx.obj['DB']))

if __name__ =="__main__":
    main(obj={})
