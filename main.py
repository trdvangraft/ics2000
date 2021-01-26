from ics2000.Core import Hub
import os

if __name__ == "__main__":
    mac = os.getenv("MAC")
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    hub : Hub = Hub(mac, email, password)