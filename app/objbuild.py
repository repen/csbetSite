from collections import namedtuple


Market = namedtuple('Market', ['name', 'left', 'right', 'winner', 'time_snapshot' ])


class Fixture:
    def __init__(self,*args):
        self.qid    = args[0]
        self.m_id   = args[1]
        self.m_time = args[2]
        self.team01 = args[3]
        self.team02 = args[4]
        self._name_markets = set()
        # self._markets = []
        self._snapshots = []

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