import os

BASE_DIR = os.getenv('BASE_DIR', os.getcwd())
PRODUCTION_WORK = os.getenv("EXTERNAL_WORK", False)
WORK_DIR = BASE_DIR
DATA_DIR = os.getenv("DATA_DIR", "/home/repente/prog/python/kwork/parsers/betsgov2/parser/data")