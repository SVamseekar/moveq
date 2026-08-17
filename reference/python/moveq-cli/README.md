# moveq-cli

Command-line tool for `moveq` — compute equity metrics from a CSV without
writing Python.

```bash
pip install moveq-cli

moveq gini data.csv --value trips --weight population
moveq palma data.csv --value trips --weight population
moveq ci data.csv --value trips --rank deprivation_rank --weight population
```
