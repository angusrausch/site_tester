import argparse
import asyncio
import httpx
import random
import re
import time
from urllib.parse import urljoin, urlparse
from statistics import mean
from enum import Enum

class RequestType(Enum):
    GET = "get"
    POST = "post"


class AsyncApp:
    def __init__(self, args):
        self.url = self._normalize_url(args.url)
        self.total_requests = args.number
        self.follow_links = args.follow_links
        self.concurrency = args.processes
        self.filters = ["http", "static/", "cdn/", "googleapis", "."]
        self.link_regex = re.compile(r'href="([^"]*)"')
        self.times = []
        self.lock = asyncio.Lock()
        self.sites_visited = []
        self.request_type = RequestType(args.type.lower())
        self.request_func = self._get_request_func()

    def _get_request_func(self):
        if self.request_type == RequestType.GET:
            return lambda client, url: client.get(url)
        elif self.request_type == RequestType.POST:
            return lambda client, url: client.post(url, data={})

    @staticmethod
    def _normalize_url(url):
        if not url.startswith(("http://", "https://")):
            print('No protocol given. Defaulting to "https"')
            return f"https://{url}"
        return url

    def check_url(self):
        print(f"Probing: {self.url}")
        try:
            start = time.perf_counter()
            response = httpx.get(self.url, timeout=10)
            duration = time.perf_counter() - start
            return response.status_code == 200, duration
        except Exception as e:
            print(f"Error probing URL: {e}")
            return False, 0

    async def run(self):
        ok, self.check_time = self.check_url()
        if not ok:
            print("Initial URL check failed.")
            return

        # Calculate how many requests each worker should perform
        requests_per_worker = self.total_requests // self.concurrency
        remainder = self.total_requests % self.concurrency

        tasks = []
        for i in range(self.concurrency):
            count = requests_per_worker + (1 if i < remainder else 0)
            tasks.append(self.worker(count))
        await asyncio.gather(*tasks)

        self.report()

    async def worker(self, request_count):
        url = self.url
        async with httpx.AsyncClient(timeout=10) as client:
            for _ in range(request_count):
                url = await self.make_request(url, client)


    async def make_request(self, url, client):
        try:
            start = time.perf_counter()
            if url is None:
                url = self.url
            response = await self.request_func(client, url)
            duration = time.perf_counter() - start

            if response.status_code != 200 and self.request_type == "get":
                print(f"[WARN] {url} returned {response.status_code} in {duration:.2f}s | adding to blacklist")
                self.filters.append(urlparse(url).path)
                return self.url

            async with self.lock:
                self.times.append(duration)

            if self.follow_links:
                return self.pick_next_url(response.text)
            return self.url

        except Exception as e:
            print(f"[ERROR] Failed request to {url}: {e}")
            return self.url

    def pick_next_url(self, html):
        links = self.link_regex.findall(html)
        valid_links = [link for link in links if not any(f in link for f in self.filters)]
        if not valid_links:
            return self.url
        new_url = urljoin(self.url, random.choice(valid_links))
        if new_url not in self.sites_visited:
            self.sites_visited.append(new_url)
        return 

    def report(self):
        if not self.times:
            print("No successful requests recorded.")
            return

        avg = mean(self.times)
        max_time = max(self.times)
        print(f"Connected to {self.url} (initial check in {self.check_time:.2f}s)")

        print(f"\nCompleted {len(self.times)} requests.")
        print(f"Average response time: {avg:.3f}s")
        print(f"Maximum response time: {max_time:.3f}s")
        if self.follow_links:
            print(f"This included {len(self.sites_visited)} unique sites")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Async Website Performance Tester")
    parser.add_argument("--url", type=str, required=True, help="Target URL to test")
    parser.add_argument("-f", "--follow-links", action="store_true", help="Follow hyperlinks on the page")
    parser.add_argument("-n", "--number", type=int, default=100, help="Total number of requests to make")
    parser.add_argument("-p", "--processes", type=int, default=10, help="Number of concurrent workers")
    parser.add_argument("--type", type=str, choices=["get", "post"], default="get",help="HTTP method to use: get or post")
    args = parser.parse_args()
    app = AsyncApp(args)
    asyncio.run(app.run())
