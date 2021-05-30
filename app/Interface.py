from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class IParams:
    time: Tuple[int]
    num_snapshot: int
    t1name: str
    t2name: str
    name_market: str
    sum_t1: int
    sum_t2: int

@dataclass
class IMarket:
    m_id:int
    c_id:int
    m_snapshot_time:int
    left_value:int
    name:str
    right_value:int


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

@dataclass
class IFixture:
    m_id:int
    m_timestamp:int
    m_team1:str
    m_team2:str
    m_league:str
    markets: List[IMarketResult]

@dataclass
class IResult:
    c_id:int
    winner:str
    score:str






