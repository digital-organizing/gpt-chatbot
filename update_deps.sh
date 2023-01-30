#!/usr/bin/sh

pip-compile -o requirements/prod.txt --upgrade pyproject.toml --resolver=backtracking
pip-compile --extra dev -o requirements/dev.txt --upgrade pyproject.toml --resolver=backtracking

pip install -r requirements/prod.txt
pip install -r requirements/dev.txt
