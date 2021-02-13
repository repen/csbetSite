from peewee import *
from Globals import  DATA_DIR
import os
from ZODB import FileStorage, DB
from persistent import Persistent
from collections import namedtuple



db = SqliteDatabase(os.path.join( DATA_DIR, "csbet.db") )

icsgame   = namedtuple("icsgame",   ["m_id", "m_time", "team1", "team2"])
fn_fixture = namedtuple("fn_fixture",   ["m_id", "m_time", "team01", "team02", "name_markets", "markets"])
Market = namedtuple('Market', ['name', 'left', 'right', 'winner', 'time_snapshot' ])


# storage = FileStorage.FileStorage(
#     os.path.join( DATA_DIR, "mydatabase.fs"), pack_keep_old=False, read_only=True )
# zopedb = DB(storage, large_record_size=1000000000000)

def get_db():
    storage = FileStorage.FileStorage(
        os.path.join( DATA_DIR, "mydatabase.fs"), read_only=True )
    zopedb = DB(storage)
    return zopedb

class RWFixture:
    def __init__(self, data):
        for key, value in data.items():
            if key == "m_time":
                setattr(self, key, int(value))
            elif key == "_snapshots":
                nd = [ { k:Market(**v) for k, v in markets.items() } for markets in value]
                setattr(self, key, nd)
            else:
                setattr(self, key, value)


    @property
    def markets(self):
        return self._snapshots

    @markets.setter
    def markets(self, elements):
        self._snapshots.append( elements )

    @markets.getter
    def markets(self):
        return self._snapshots

    @property
    def name_markets(self):
        return self._name_markets

    @name_markets.setter
    def name_markets(self, names):
        for name in names:
            self._name_markets.add( name )

    @name_markets.getter
    def name_markets(self,):
        return self._name_markets



class CSGame(Model):
    m_id     = CharField()
    m_time   = IntegerField()
    team1    = CharField()
    team2    = CharField()

    class Meta:
        database = db


class ITCSGame(Persistent):
    def __init__(self):
        zopedb = get_db()

        connection = zopedb.open()
        root = connection.root()
        self.data = root["csgame"].csgame
        # breakpoint()
        # self.csgame = {}

    def get_csgame(self):
        data = []
        for cs in self.data.values():
            cs["m_time"] = int(cs["m_time"])
            data.append(cs)

        return [ icsgame(**val) for val in data ]

class Finished(Persistent):

    def __init__(self):
        zopedb = get_db()
        connection = zopedb.open()
        root = connection.root()
        self.tree = root["finished"].tree

    def get_fixtures(self):
        for key, fixture in self.tree.items():
            yield fixture

    def get_all_keys(self):
        return list( self.tree.keys() )

    def get_fixture(self, fixture_id):
        fixture = self.tree.get(fixture_id)
        # breakpoint()
        return RWFixture(fixture) if fixture else False





# ICSGame = ITCSGame()
# finished = Finished()
# breakpoint()



if __name__ == '__main__':
    pass
