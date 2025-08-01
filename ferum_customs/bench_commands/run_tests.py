import os
import sys
import click
import pytest
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

@click.command()
@click.argument('app')
@click.argument('test_path', type=str)
def run_tests(app: str, test_path: str):
    # Directory Traversal Protection
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app_path = os.path.abspath(os.path.join(base_dir, app))
    test_path = os.path.abspath(os.path.join(base_dir, test_path))

    if not app_path.startswith(base_dir) or not test_path.startswith(base_dir):
        raise click.ClickException("Invalid path: potential directory traversal detected.")

    # Environment Variable Handling
    original_site_name = os.environ.get("SITE_NAME")
    os.environ["SITE_NAME"] = app

    try:
        # Logging the start of the test
        logging.info(f"Running tests for app: {app} at path: {test_path}")

        # Run tests and handle potential exceptions
        try:
            exit_code = pytest.main([test_path])
        except Exception as e:
            logging.error(f"An error occurred while running tests: {e}")
            raise click.ClickException(f"An error occurred while running tests: {e}")

        # Return or exit with the appropriate exit code
        sys.exit(exit_code)
    finally:
        # Restore the original environment variable
        if original_site_name is not None:
            os.environ["SITE_NAME"] = original_site_name
        else:
            del os.environ["SITE_NAME"]

if __name__ == '__main__':
    run_tests()
