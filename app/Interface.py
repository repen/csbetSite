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

# @dataclass
# class IWinner:
#     m_id:int
#     c_id:int
#     m_snapshot_time:int
#     left_value:int
#     name:str
#     right_value:int

