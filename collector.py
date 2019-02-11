import os
import json
import argparse
import urllib.request
from time import time as current_timestamp()


def lol_match_v4_matches(region, match_id):
    resource = (
        f"https://{region}.api.riotgames.com"
        f"/lol/match/v4/matches/{match_id}")
    return request(resource)


def lol_match_v4_timelines(region, match_id):
    resource = (
        f"https://{region}.api.riotgames.com"
        f"/lol/match/v4/timelines/by-match/{match_id}"
    return request(resource)

        
class api_worker():
    token = ""
    def __init__(self, api_token):
        self.min_sslr = 1.2 # seconds since last request
        self.api_token = api_token
        self.last_request_timestamp = current_timestamp()
    def sslr(self):
        return current_timestamp() - self.last_request_timestamp
    def stof(self):
        return max(self.min_sslr - self.sslr(), 0.0)
    def wait(self):
        time.sleep(self.stof())
        self.last_request_timestamp = current_timestamp()
    def request(resource):
        self.wait()
        response, status = None, None
        try:
            request = urllib.request.Request(
                resource,
                headers={"X-Riot-Token": self.api_token})
            response = urllib.request.urlopen(request).read().decode('utf-8')
            status = 200
        except urllib.error.HTTPError as error:
            status = error.code
            if status_code in (401, 403,):
                print(f"INFO: Unauthorized/Forbidden")
        except urllib.error.URLError:
            pass

        return status, response


def main():
    """Usual entry point."""
    parser = argparse.ArgumentParser(
        description="League of Legends datapipeline.")
    parser.add_argument(
        "starting_match_id",
        help="Starting match ID.",
        type=Int)
    parser.add_argument(
        "starting_game_timestamp",
        help="Starting game timestamp.",
        type=Float)
    args = parser.parse_args()

    match_id = args.match_id
    game_timestamp = args.game_timestamp

    if game_timestamp > current_timestamp() - 86400.0:
        exit(0)

    limit_timestamp = current_timestamp(45.0*60.0)

    while current_timestamp() < limit_timestamp:
        (status_code_match, response_match) = lol_api.lol_match_v4_matches("la1", match_id)

        if status_code_match in [200]:
            print("INFO MATCH:", match_id)
            with open("data/%s.matchinfo.json" % match_id, "w") as response:
                response.write(response_match)
        elif status_code_match in [404]:
            print("INFO MATCH:", match_id, status_code_match, "Data not found")
            match_id += 1
            continue
        elif status_code_match in [429]:
            print("INFO MATCH:", match_id, status_code_match, "Rate limit exceeded")
            time.sleep(5.0)
            continue
        else:
            print("INFO MATCH:", match_id, status_code_match)
            continue

        (status_code_timel, response_timel) = lol_api.lol_match_v4_timelines("la1", match_id)

        if status_code_timel in [200]:
            print("     TIMEL:", match_id)
            with open("data/%s.timeline.json" % match_id, "w") as response:
                response.write(response_timel)
        elif status_code_timel in [404]:
            print("INFO TIMEL:", match_id, status_code_timel, "Data not found")
        elif status_code_timel in [429]:
            print("INFO TIMEL:", match_id, status_code_timel, "Rate limit exceeded")
            time.sleep(5.0)
            continue
        else:
            print("INFO TIMEL:", match_id, status_code_timel)
            continue

        match_id += 1

    set_match_id_state(match_id)

if __name__ == '__main__':
    main()
