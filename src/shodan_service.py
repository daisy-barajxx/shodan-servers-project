import signal
import sys
import time
import requests
import os
from datetime import datetime

class ShodanService:
    def __init__(self):
        self.output_file = "/tmp/shodan_servers.out"
        self.api_key = os.getenv("SHODAN_API_KEY")   # Should be configurable
        self.interval = 3600  # 1 hour between polls

    def signal_handler(self, sig, frame):
        with open(self.output_file, 'a') as f:
            f.write("Received SIGTERM, exiting\n")
            f.flush()
            print("", flush=True)
        sys.exit(0)

    def fetch_servers(self):
        try:
            url = f'https://api.shodan.io/shodan/host/search?key={self.api_key}&query=apache%20state:WA'
            response = requests.get(url)
            data = response.json()
            with open(self.output_file, 'w') as f:
                if 'matches' in data:
                    for match in data['matches']:
                        ip = match.get('ip', 'N/A')
                        city = match.get('location', {}).get('city', 'N/A')
                        f.write(f"{city}, {ip}\n")
                else:
                    raise ValueError("No 'matches' in API response")
        except Exception as e:
            with open(self.output_file, 'a') as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Error - {str(e)}\n")

    def run(self):
        signal.signal(signal.SIGTERM, self.signal_handler)
        while True:
            self.fetch_servers()
            time.sleep(self.interval)

if __name__ == "__main__":
    service = ShodanService()
    service.run()