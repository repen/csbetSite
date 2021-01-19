from peewee import *
from Globals import  DATA_DIR
import os
db = SqliteDatabase(os.path.join( DATA_DIR, "csbet.db") )

class CSGame(Model):
    m_id     = CharField()
    m_time   = IntegerField()
    team1    = CharField()
    team2    = CharField()

    class Meta:
        database = db


if __name__ == '__main__':
    pass
