#!/bin/bash
cd "$(dirname "$0")"
python3 -m flask --app app run --host=0.0.0.0 --port=5000 &
sleep 2
xdg-open http://localhost:5000
wait
