import os

BASE_DIR = os.getenv('BASE_DIR', os.getcwd())
PRODUCTION_WORK = os.getenv("EXTERNAL_WORK", False)
HOST = os.getenv("HOSTMQ", "95.217.181.200")
WORK_DIR = BASE_DIR
DATA_DIR = os.getenv("DATA_DIR", os.path.join( BASE_DIR, "data" ))