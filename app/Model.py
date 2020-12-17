from peewee import *
from Globals import WORK_DIR

db = SqliteDatabase(WORK_DIR + "/data/database/csgo02.db")


class CSGame(Model):
    m_id     = CharField()
    m_time   = IntegerField()
    team1    = CharField()
    team2    = CharField()

    class Meta:
        database = db


if __name__ == '__main__':
    pass
