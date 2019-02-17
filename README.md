# League-of-Legends-Datapipeline
A python data pipeline for the League of Legends game.

It will fetch sequentially:
- match information: `/lol/match/v4/matches/{matchId}`
- match timeline: `/lol/match/v4/timelines/by-match/{matchId}`

And produces an stream of formatted output of CSV schemas and records.

The CSV can later be loaded to a data warehouse
like Amazon Redshift, a MySQL instance, among others.

# How to use
First create an initial `state.json` file.

```json
{
    "match_id": 1000000000,
    "region": "na1",
    "api_token": "RGAPI-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
}
```

`match_id` indicates the match ID from which to start fetching.

The data pipeline reads the state from stdin:

```bash
cat state.json | ./datapipeline.py
```

And output a final state to stdout:

```bash
(cat state.json | ./datapipeline.py) > new_state.json
```

if successful the new state will be some match IDs ahead of the initial state, and the data will be stored locally.

if not successful the new state will be the same initial state.

Putting it all together:

```bash
# if the pipeline went well
if (cat state.json | ./datapipeline.py) > new_state.json; then
  # update the state
  mv new_state.json state.json
  # condensate everything
  ./condensate.py
fi
```

This will use the state file that you just created,
produce output that can be loaded to your data warehouse
(or rendered locally with any CSV visor like LibreOffice)
and update the statefile if succeded.

Run this process in a loop to continually fetch data.
