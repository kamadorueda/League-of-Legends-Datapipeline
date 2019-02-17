# League-of-Legends-Datapipeline
A python data pipeline for the League of Legends game.

It will fetch sequentially:
- match information: `/lol/match/v4/matches/{matchId}`
- match timeline: `/lol/match/v4/timelines/by-match/{matchId}`

And produces an stream of formatted output that can be loaded to a data warehouse
like Amazon Redshift, or a MySQL database.

# How to use
First create an initial `state.json` file.

```json
{
    "match_id": 1000000000,
    "region": "na1",
    "api_token": "RGAPI-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
}
```

Now you are ready to run the data pipeline:

```bash
# if the pipeline went well
if (cat state.json | ./datapipeline.py) > new_state.json; then
  # update the state
  mv new_state.json state.json
fi
```

This will use the state file that you just created,
produce output that can be loaded to your data warehouse (ETL),
and update the statefile if succeded.
