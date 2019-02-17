#!/usr/bin/env bash

# if the pipeline went well
if (cat state.json | ./datapipeline.py) > new_state.json; then
  # update the state
  mv new_state.json state.json
fi
