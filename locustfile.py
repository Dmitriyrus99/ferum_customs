from locust import HttpUser, between, task


class WebsiteUser(HttpUser):  # type: ignore[misc]
    wait_time = between(1, 5)

    @task  # type: ignore[misc]
    def health(self) -> None:
        self.client.get("/health")
