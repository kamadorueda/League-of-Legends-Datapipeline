#!/usr/bin/env python3

import io
import os
import sys
import json
import argparse
import urllib.request
from time import sleep
from time import time as curr_timestamp

if not os.path.isdir("data"):
    os.makedirs("data")

def json_as_string(obj):
    return json.dumps(obj, indent=4)

def print_stderr(message):
    print(message, file=sys.stderr, flush=True)

def print_stdout(message):
    print(message, file=sys.stdout, flush=True)

class API_Worker():
    def __init__(self, region, api_token):
        self.min_sslr = 1.2 # min seconds since last request
        self.lrts = curr_timestamp() # last request timestamp
        self.api_token = api_token
        self.api_url = f"https://{region}.api.riotgames.com"
    def request(self, resource):
        # wait needed time to not exceed the rate limit
        sleep(max(
            + self.min_sslr
            + self.lrts
            - curr_timestamp(), 0.0))
        self.lrts = curr_timestamp()

        response, status = None, None
        try:
            request = urllib.request.Request(
                resource,
                headers={"X-Riot-Token": self.api_token})
            response = urllib.request.urlopen(request).read().decode('utf-8')
            status = 200
        except urllib.error.HTTPError as error:
            status = error.code
            if status == 429:
                print_stderr(f"INFO: [WORKER] [SLEEP]")
                sleep(self.min_sslr)
                return request(resource)
        except urllib.error.URLError:
            pass
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
    game_timestamp = state["game_timestamp"]
    worker = API_Worker(state["region"], state["api_token"])

    if game_timestamp > curr_timestamp() - 86400.0:
        print_stdout(json_as_string(state))

    limit_timestamp = curr_timestamp() + 1.0*10.0

    while curr_timestamp() < limit_timestamp:
        status_match, response_match = \
            worker.lol_match_v4_matches(match_id)

        if status_match == 200:
            print_stderr(f"INFO: [MATCH] [{match_id}]")
            with open(f"data/{match_id}.matchinfo.json", "w") as response:
                response.write(response_match)
            game_timestamp = json.loads(response_match)["gameCreation"] / 1000.0
        elif status_match == 404:
            print_stderr(f"INFO: [MATCH] [{match_id}] [{status_match}] [Data not found]")
            match_id += 1
            continue
        elif status_match in [401, 403]:
            print_stderr("INFO: Unauthorized/Forbidden")
            print_stdout(json_as_string(state))
            exit(1)
        else:
            print_stderr(f"INFO: [MATCH] [{match_id}] [{status_match}]")
            continue

        status_timeline, response_timeline = \
            worker.lol_match_v4_timelines(match_id)

        if status_timeline == 200:
            print_stderr(f"INFO: [TIMEL] [{match_id}]")
            with open(f"data/{match_id}.timeline.json", "w") as response:
                response.write(response_timeline)
        elif status_timeline in [401, 403]:
            print_stderr("INFO: Unauthorized/Forbidden")
            print_stdout(json_as_string(state))
            exit(1)
        else:
            print_stderr(f"INFO: [TIMEL] [{match_id}] [{status_match}]")
            continue

        match_id += 1

    new_state = {
        "match_id": match_id,
        "game_timestamp": game_timestamp,
        "region": state["region"],
        "api_token": state["api_token"]
    }
    print_stdout(json_as_string(new_state))
    print_stderr(json_as_string(new_state))


if __name__ == '__main__':
    main()
