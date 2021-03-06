from dataclasses import dataclass, field

@dataclass
class IFixture:
    m_id:int
    m_timestamp:int
    m_team1:str
    m_team2:str
    m_league:str

@dataclass
class IMarket:
    m_id:int
    c_id:int
    m_snapshot_time:int
    left_value:int
    name:str
    right_value:int

@dataclass
class IResult:
    c_id:int
    winner:str
    score:str

@dataclass
class IMarketResult:
    m_id:int
    c_id:int
    m_snapshot_time:int
    left_value:int
    name:str
    right_value:int
    winner:str
    score:str



# (124180, 272817, 272817, 1613527127, 76188, 'Main', 35014, | 368, 272817, 'right', '0 : 2')



