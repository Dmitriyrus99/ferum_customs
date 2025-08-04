import logging

from locust import HttpUser, between, task


class WebsiteUser(HttpUser):
    """User class for load testing the website."""

    wait_time: between = between(1, 5)

    @task
    def health(self) -> None:
        """Task to check the health of the application."""
        response = self.client.get("/health")
        if response.status_code != 200:
            logging.error(
                f"Health check failed with status code {response.status_code}"
            )
