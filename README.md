# League-of-Legends-Datapipeline
A python data pipeline for the League of Legends game.

it fetches sequentially:
- match information: `/lol/match/v4/matches/{matchId}`
- match timeline: `/lol/match/v4/timelines/by-match/{matchId}`

and produces an stream of formatted output that can be loaded to a data warehouse
like Amazon Redshift, or a MySQL database.

# How to use
First create an initial `state.json` file,
you can leave game_timestamp as 0.0 for the first sync:

```json
{
    "match_id": 1000000000,
    "game_timestamp": 0.0,
    "region": "na1",
    "api_token": "RGAPI-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
}
```

Now you are ready to run the data pipeline:

```bash
$ cat state.json | ./datapipeline.py > new_state.json && mv --force {new_,}state.json
```

This will use the state file that you just created,
produce output that can be loaded to your data warehouse (ETL),
and update the statefile if succeded.
