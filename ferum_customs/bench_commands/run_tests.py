import os

import click
import pytest


@click.command("run-tests")
@click.option("--site", required=True, help="Site name on which to run tests")
@click.option("--app", required=True, help="App name to test")
@click.option(
    "--test",
    "test_path",
    default="tests/unit",
    help="Test path relative to app, e.g., tests/unit",
)
def run_tests(site, app, test_path):
    """Run pytest tests for the specified app."""
    # Ensure SITE_NAME is set for any fixtures or configurations
    os.environ["SITE_NAME"] = site
    path = os.path.join(app, test_path)
    # Execute pytest on the target path
    exit(pytest.main([path]))
