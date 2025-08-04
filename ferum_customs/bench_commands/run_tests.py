import logging
import os
import sys
from typing import Optional

import click
import pytest

# Configure logging
logging.basicConfig(level=logging.INFO)


@click.command()
@click.argument("app", type=str)
@click.argument("test_path", type=str)
def run_tests(app: str, test_path: str) -> None:
    """
    Run tests for the specified app at the given test path.

    :param app: The name of the app to test.
    :param test_path: The path to the test files.
    :raises click.ClickException: If there is a directory traversal attempt or test execution failure.
    """
    # Directory Traversal Protection
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    app_path = os.path.abspath(os.path.join(base_dir, app))
    test_path = os.path.abspath(os.path.join(base_dir, test_path))

    if not app_path.startswith(base_dir) or not test_path.startswith(base_dir):
        raise click.ClickException(
            "Invalid path: potential directory traversal detected."
        )

    # Environment Variable Handling
    original_site_name: str | None = os.environ.get("SITE_NAME")
    os.environ["SITE_NAME"] = app

    try:
        # Logging the start of the test
        logging.info(f"Running tests for app: {app} at path: {test_path}")

        # Run tests and handle potential exceptions
        exit_code = run_pytest(test_path)

        # Return or exit with the appropriate exit code
        sys.exit(exit_code)
    finally:
        # Restore the original environment variable
        if original_site_name is not None:
            os.environ["SITE_NAME"] = original_site_name
        else:
            os.environ.pop("SITE_NAME", None)


def run_pytest(test_path: str) -> int:
    """Run pytest on the specified test path.

    :param test_path: The path to the test files.
    :return: The exit code from pytest.
    :raises click.ClickException: If an error occurs while running tests.
    """
    try:
        return pytest.main([test_path])
    except Exception as e:
        logging.error(f"An error occurred while running tests: {e}")
        raise click.ClickException(f"An error occurred while running tests: {e}")


if __name__ == "__main__":
    run_tests()
