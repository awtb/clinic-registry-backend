#!/bin/sh

export PYTHONPATH=$(pwd)/src:$PYTHONPATH

python -m alembic upgrade head
python -m clinic_registry --reload --host=localhost