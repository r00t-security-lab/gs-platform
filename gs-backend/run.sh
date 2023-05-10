#! /bin/bash
cd /gs-backend
flask db upgrade
python ./run_worker_api.py &
python ./run_reducer_admin.py