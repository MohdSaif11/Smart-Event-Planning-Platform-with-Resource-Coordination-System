from locust import HttpUser, task

class EventUser(HttpUser):

    @task
    def view_events(self):
        self.client.get("/api/events/")
