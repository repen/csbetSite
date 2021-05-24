import os, re, hashlib
from typing import List
from Interface import IFixture

def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


def hash_(string):
    return hashlib.sha1(string.encode()).hexdigest()


def get_search(param, objs: List[IFixture]):
    # {'time': '2020-07-21:2020-07-22', 'name_market': '', 't1name': '', 't2name': '', 'sum_t1': '100', 'sum_t2': '100', 'num_snapshot': '5'}
    param_examp = {
        "time" : (0,0),
        "num_snapshot" : 5, #5
        "t1name" : "",
        "t2name" : "",
        "name_market" : "[Карта #2] Первый пистолетный раунд",
        "sum_t1" : 0,
        "sum_t2" : 0,
    }

    result = objs
    l = list
    f = filter

    if param["league"] != "-":
        result = l( f ( lambda x : x.m_league == param["league"], result) )
    # if param['time'][0] and param['time'][1]:
    #     result = l( f ( lambda x : x.m_timestamp > param['time'][0] and x.m_timestamp < param['time'][1], result) )

    if param['t1name']:
        result = l( f( lambda x : param['t1name'] in x.m_team1, result) )

    if param['t2name']:
        result = l( f( lambda x : param['t2name'] in x.m_team2, result) )

    if param['name_market']:
        result = l( f(
            lambda x : True in map(
                lambda market: market.name == param["name_market"] , x.markets ),
            result)
        )
        for res in result:
            res.markets = list( filter( lambda x: x.name == param["name_market"], res.markets) )

    if param['sum_t1']:
        '''Добавить фильтр для всех рынков'''
        if param["name_market"]:
            result = l(f( lambda x: x.markets[0].left_value >= param["sum_t1"] , result) )
        else:
            for res in result:
                res.markets = l(f( lambda market: market.left_value >= param["sum_t1"], res.markets ))

    if param['sum_t2']:
        if param["name_market"]:
            result = l(f( lambda x: x.markets[0].right_value >= param["sum_t2"] , result) )
        else:
            for res in result:
                res.markets = l(f( lambda market: market.right_value >= param["sum_t2"], res.markets ))

    # =============== Delete defective fixtures
    index_temp = []
    for e, res in enumerate( result ):
        for ee, market in enumerate( res.markets ):

            if market.name == "Main":
                if not re.search(r"^\d+\s\:\s\d+$", market.score):
                    index_temp.append( (e, ee) )
                    break

            if "Победа на карте" in market.name:
                if not market.score:
                    index_temp.append( (e, ee) )
                    break

    new_res = []
    it = 0
    for e, res in enumerate( result ):

        if it < len(index_temp):
            if index_temp[it][0] == e and index_temp[it][1] == 0:
                it+=1
                continue
            
            if index_temp[it][0] == e and index_temp[it][1] > 0:
                res.markets.pop( index_temp[it][1] )
                it+=1
       
        new_res.append(res)

    result = new_res
    # =============== delete defective fixtures

    return result


def divider(arr):
    '''
    разрезать массив по времени
    60 минут = 1 минута
    6-1 = 30 минут
    24-6 = 60 
    72-24 = 120
    '''
    result = []
    r0_1 = arr[-60:]
    r0_2 = arr[-360:-60]
    r0_3 = arr[-1440:-360]
    r0_4 = arr[-5000:-1440]

    if r0_1:
        r0_1 = [ x for e, x in enumerate(r0_1) ]

    if r0_2:
        r0_2 = [ x for e, x in enumerate(r0_2) if e % 30 == 0]

    if r0_3:
        r0_3 = [ x for e, x in enumerate(r0_3) if e % 60 == 0]

    if r0_3:
        r0_4 = [ x for e, x in enumerate(r0_4) if e % 120 == 0]

    result.extend( r0_4 )
    result.extend( r0_3 )
    result.extend( r0_2 )
    result.extend( r0_1 )

    return result