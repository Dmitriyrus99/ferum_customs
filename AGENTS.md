# Repository Guidelines

CI uses a Docker-based stack defined in `docker-compose.yml`. Workflows start containers using this stack to run tests.

### Quick local unit tests

1. Install dev dependencies: `pip install -r requirements-dev.txt`.
2. From your bench directory run:

   ```bash
   bench --site <site> run-tests --app ferum_customs --tests-path tests/unit
   ```

This targets only `tests/unit` for a fast feedback loop.
