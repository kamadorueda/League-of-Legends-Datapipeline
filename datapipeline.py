#!/usr/bin/env python3

import io
import os
import sys
import json
import structura
import urllib.request
from time import sleep
from time import time as curr_timestamp


def json_as_string(obj):
    return json.dumps(obj, indent=4)


def print_stderr(message):
    print(message, file=sys.stderr, flush=True)


def print_stdout(message):
    print(message, file=sys.stdout, flush=True)


def process(endpoint_name, response):
    data = json.loads(response)
    for table, record in structura.linearize(endpoint_name, data):
        print_stderr(json.dumps({"table": table, "record": record}, indent=2))


def stop_pipeline(state, exit_code):
    print_stdout(json_as_string(state))
    print_stderr(json_as_string(state))
    exit(exit_code)


class API_Worker():
    def __init__(self, region, api_token):
        # min seconds to wait since last request
        self.wait = 1.2
        # last request timestamp
        self.last = curr_timestamp()
        # api url and headers
        self.api_url = f"https://{region}.api.riotgames.com"
        self.api_headers = {"X-Riot-Token": api_token}

    def request(self, resource):
        # wait needed time not to exceed the rate limit
        sleep(max(
            + self.last
            + self.wait
            - curr_timestamp(), 0.0))
        self.last = curr_timestamp()

        try:
            request = urllib.request.Request(
                resource, headers=self.api_headers)
            connection = urllib.request.urlopen(request)
            status, response = 200, connection.read().decode('utf-8')
        except urllib.error.HTTPError as error:
            status, response = error.code, None
        except urllib.error.URLError:
            status, response = None, None

        return status, response

    def lol_match_v4_matches(self, match_id):
        return self.request(
            f"{self.api_url}/lol/match/v4/matches/{match_id}")

    def lol_match_v4_timelines(self, match_id):
        return self.request(
            f"{self.api_url}/lol/match/v4/timelines/by-match/{match_id}")


def main():
    """Usual entry point."""
    buffer = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
    state = json.loads(buffer.read())
    print_stderr(json_as_string(state))

    match_id = state["match_id"]
    worker = API_Worker(state["region"], state["api_token"])

    # fetch data for 60 seconds
    limit_timestamp = curr_timestamp() + 60.0

    # api endpoints
    api_endpoints = (
        ("match_info", worker.lol_match_v4_matches),
        ("match_timeline", worker.lol_match_v4_timelines),
    )

    while curr_timestamp() < limit_timestamp:
        for endpoint_name, endpoint_wrapper in api_endpoints:
            status, response = endpoint_wrapper(match_id)
            print_stderr(f"INFO: [{endpoint_name}] [{match_id}] [{status}]")
            if status == 200:
                process(endpoint_name, response)
            elif not status == 404:
                stop_pipeline(state, exit_code=1)

        match_id += 1

    # write the new state
    stop_pipeline({
        "match_id": match_id,
        "region": state["region"],
        "api_token": state["api_token"]
    }, exit_code=0)


if __name__ == '__main__':
    main()
