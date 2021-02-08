import os, re, hashlib

def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


def hash_(string):
    return hashlib.sha1(string.encode()).hexdigest()


def get_search(param, objs):
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
    # print(len(result[0].markets), "!!!!!!!")
    # result = l( f( lambda fx : len( fx.markets ) >  param['num_snapshot'], result ) )
    # breakpoint()

    if param["league"] != "-":
        result = l( f ( lambda x : x.league == param["league"], result) )

    if param['time'][0] and param['time'][1]:
        result = l( f ( lambda x : x.m_time > param['time'][0] and x.m_time < param['time'][1], result) )

    if param['t1name']:
        result = l( f( lambda x : param['t1name'] in x.team01, result) )

    if param['t2name']:
        result = l( f( lambda x : param['t2name'] in x.team02, result) )

    if param['name_market']:
        def name_processing_market(m):
            markets = m.name_markets

            last_names = set( x.name for x in m.markets[-1].values() )
            markets.update( last_names )
            
            result = False
            for name in markets:


                if re.search( r"выигра\w+ одну карту", param['name_market']):
                    result = True
                    break


                if re.search( "^{}".format(param['name_market']), name) or param['name_market'] == name:
                    # if "Количество раундов 26.5" == name:
                    #     import pdb;pdb.set_trace();

                    result = True
                    break
                

            return result
        # result = l( f( lambda x : param['name_market'] in x.name_markets, result)  )
        result = l( f( name_processing_market, result)  )


    def check_sum(sum_, mode, arr):

        arr_obj = arr.values()
        res = l( f( lambda x: param['name_market'] in x.name, arr_obj) )
        if res:
            market = res[0]

            if mode == 1:
                return market.left  >= sum_
            if mode == 2:
                return market.right >= sum_
        return False
    
    if param['sum_t1']:
        result = l ( f(
            lambda x: check_sum( param['sum_t1'], 1, x.markets[ 0 ] ), result ) )

    if param['sum_t2']:
        result = l ( f(
            lambda x: check_sum( param['sum_t2'], 2, x.markets[ 0 ] ), result ) )
    return result