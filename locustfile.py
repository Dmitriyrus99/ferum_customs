from locust import HttpUser, between, task

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def health(self) -> None:
        response = self.client.get("/health")
        if response.status_code != 200:
            response.failure(f"Health check failed with status code {response.status_code}")
