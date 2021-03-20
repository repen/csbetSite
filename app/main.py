from flask import Flask, render_template, request, g
import os, re, logging, time
# from Model import ITCSGame, Finished, RWFixture, Fixture
from Model import Fixture, Market, Result, Koef, db
from datetime import datetime
from Globals import PRODUCTION_WORK, DATA_DIR
from tools import get_search, divider
import itertools
from waitress import serve
from flask_caching import Cache
from Interface import IFixture, IMarket, IResult, IMarketResult


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


logger = logging.getLogger("__DEBUG__")

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "simple", # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}

pattern001 = r"выигра\w+ \d+ раун\w+|ножом|убийство|выигра\w+ две|три карт\w|ACE|pro100"

app = Flask(__name__)

app.config.from_mapping(config)
cache = Cache(app)

OBJECT_DIR = os.path.join( DATA_DIR, "objects")

def timeit(f):

    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        logger.info("Time {} {}".format(te-ts, str(f)) )
        return result

    return timed

@app.context_processor
def utility_processor():
    def search_markets(array, name):
        result = False
        array = [x for x in array if x.name == name]
        if array:
            result = array[0]
        return result

    def time_human(timestamp):
        if isinstance(timestamp, dict):
            for s in timestamp:
                # timestamp[s].time_snapshot
                return datetime.fromtimestamp( timestamp[s].time_snapshot ).strftime("%Y.%m.%d %H:%M")

        return datetime.fromtimestamp( timestamp ).strftime("%Y.%m.%d %H:%M")

    def rename_market(market):

        result = None
        for name in market.keys():
            search = re.search( r"выигра\w+ одну карту", name)
            if search:
                result = name
                break

        return result
    def if_in(a,b):
        if isinstance(a, int):
            return a <= b
        if isinstance(a, str):
            return a in b and not re.search( pattern001, b )
        return False
    def swap_result(name, markets, result):
        replace_result = result

        if re.search(r"Количество карт \d\.\d", name):
            replace_result = markets[ 'Main' ].winner

        if re.search(r"^Количество раундов 26\.5", name):
            replace_result = markets[ name.replace("Количество раундов 26.5", "Main") ].winner
        
        if re.search(r"(?!^)Количество раундов 26\.5", name):
            replace_result = markets[ name.replace("Количество раундов 26.5", "Победа на карте") ].winner
        
        return str( replace_result )

    return dict(search_markets=search_markets, time_human=time_human, 
        rename_market=rename_market, if_in = if_in, swap_result = swap_result)

def convert_date(string):
    start = string.split(":")[0]
    end = string.split(":")[1]
    return (int( datetime.strptime(start, "%Y-%m-%d").timestamp()), int( datetime.strptime(end, "%Y-%m-%d").timestamp() ))

def name_markets_prepare(fixtures):
    pattern01 = r"выиграют одну карту|выиграет одну карту"
    def win_single_map(name_market):
        search = re.findall(pattern01, name_market)
        if search:
            # print(name_market, search)
            name_market = "выиграют одну карту"
        
        return name_market
    
    name_markets = set( itertools.chain.from_iterable( [x.name_markets for x in fixtures] ) )
    name_markets = set( map(win_single_map , name_markets ) )

    name_markets = sorted( name_markets )
    
    return name_markets

# @timeit
# def load_objects(*args, **kwargs):
#     index = kwargs.setdefault("index", -1)
#     fixtures = []
#     finished = Finished()
#     for fixture in finished.get_fixtures():
#         fixture = RWFixture(fixture)
#         try:
#             fixture._snapshots = [ fixture._snapshots[ index ] ]
#             fixtures.append(fixture)
#         except IndexError as ie:
#             print("IndexError", ie)
#     finished.zopedb.cacheMinimize()
#     finished.zopedb.close()
#     return fixtures


# @cache.cached(timeout=60*60*5, key_prefix='load_objects_cache')
# def load_objects_cache():
#     fixtures = load_objects()
#     data = {}
#     ts = time.time()
#     data["name_markets"] = name_markets_prepare( fixtures )
#     data["name_markets"] = list( filter(lambda x: not re.search(pattern001, x), data["name_markets"] ) )
#     data["teams"] = sorted( set( itertools.chain.from_iterable( [ [x.team01, x.team02] for x in fixtures] ) ) )
#     data["league"] = set( x.league for x in fixtures )
#     te = time.time()
#
#     logger.info("Time {}".format(te-ts) )
#     return data

@app.route('/')
def index():
    data = {}
    data['fixtures'] = []


    # breakpoint()
    date = request.args.get('date', default=False)

    if date:
        start_day = datetime.strptime(date, "%m/%d/%Y").replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        query = Fixture.select().where(
            (Fixture.m_timestamp > start_day) & (Fixture.m_timestamp < start_day + 60*60*24 )
        ).order_by(Fixture.m_timestamp)
    else:
        current_time = datetime.now()
        start_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
        query = Fixture.select().where(Fixture.m_timestamp > start_day).order_by(Fixture.m_timestamp)

    
    for fixture in query.namedtuples():
        finished = bool(Result.select().where(Result.c_id == fixture.m_id))
        m_id = fixture.m_id
        m_team = "{} vs {}".format( fixture.m_team1, fixture.m_team2 )
        m_time = datetime.fromtimestamp( fixture.m_timestamp ).strftime("%Y.%m.%d %H:%M")
        data['fixtures'].append( ( m_id, m_team, m_time, finished ) )

    return render_template("index.html", data = data)

@app.route('/match/<m_id>')
def match_page(m_id):
    int( m_id )
    fixture = {}

    query0 = Fixture.select().where(Fixture.m_id == m_id)
    if query0:
        dfixture = query0.namedtuples()[0]._asdict()
        dfixture.pop("id")
        fixture = IFixture(**dfixture).__dict__

    # last_timestamp = db.execute_sql(f"SELECT max(m_snapshot_time) FROM market WHERE m_id = {m_id}")
    # last_timestamp = last_timestamp.fetchone()

    # query = db.execute_sql(
    #     f"SELECT * FROM market WHERE m_id = {m_id} AND m_snapshot_time IN \
    #     ( SELECT DISTINCT m_snapshot_time FROM market WHERE m_id = {m_id} \
    #         AND m_snapshot_time < (SELECT m_timestamp FROM fixture WHERE m_id = {m_id}) \
    #         OR m_snapshot_time = {last_timestamp[0]} \
    #     )"
    # )

    # query = db.execute_sql(
    #     f"SELECT * FROM market WHERE m_id = {m_id} AND m_snapshot_time IN \
    #     ( SELECT DISTINCT m_snapshot_time FROM market WHERE m_id = {m_id} \
    #         AND m_snapshot_time < (SELECT m_timestamp FROM fixture WHERE m_id = {m_id}) \
    #         OR  m_snapshot_time=(SELECT max(m_snapshot_time) FROM market WHERE m_id = {m_id}) \
    #     )"
    # )    
    
    query = db.execute_sql(
        f"SELECT * FROM market WHERE m_id = {m_id} AND m_snapshot_time IN \
        ( SELECT DISTINCT m_snapshot_time FROM market WHERE m_id = {m_id} \
            AND m_snapshot_time < (SELECT m_timestamp FROM fixture WHERE m_id = {m_id}) \
        )"
    )


    snapshot_dict = {}
    
    for row in query.fetchall():
        market = IMarket( *row[1:] )
        if market.m_snapshot_time not in snapshot_dict:
            snapshot_dict[market.m_snapshot_time] = []
        snapshot_dict[market.m_snapshot_time].append( market )

    snapshot_dict = [v for k, v in snapshot_dict.items()]

    winner = []
    if snapshot_dict:

        for market in snapshot_dict[-1]:
            query = Result.select().where( Result.c_id == market.c_id )
            data = query.namedtuples()[0]._asdict()
            data["name"] = market.name
            winner.append( data )

    # breakpoint()
    return render_template("match.html", data = {
        "snapshots" : divider( snapshot_dict ),
        "winner" : winner,
        "fixture" : fixture
    })


@app.route('/filter')
def filter_page():
    data = {}
    data['result'] = []
    params = request.args.to_dict()
    fixtures = []

    @cache.cached(timeout=60 * 60 * 50, key_prefix='team_list')
    def get_team_list():
        query1 = db.execute_sql( f"SELECT m_team1, m_team2 FROM fixture" )
        teams = set()
        for row in query1.fetchall():
            teams.add(row[0])
            teams.add(row[1])

        teams = list(teams)
        teams.sort()
        return teams

    data["teams"] = get_team_list()

    @cache.cached(timeout=60 * 60 * 50, key_prefix='league_list')
    def get_league_list():
        query2 = db.execute_sql(f"SELECT DISTINCT m_league FROM fixture")
        leagues = list( set( [x[0] for x in query2.fetchall()] ) )
        leagues.sort()
        return leagues

    data["league"] = get_league_list()

    @cache.cached(timeout=60 * 60 * 50, key_prefix='market_list')
    def get_market_list():
        query3 = db.execute_sql(f"SELECT DISTINCT name from market")
        market_name_list = [ x[0] for x in query3.fetchall()]
        market_name_list = list( filter( lambda x: not re.search(pattern001, x), market_name_list) )
        market_name_list = list( filter( lambda x: not re.search("выигра", x), market_name_list) )
        if market_name_list:
            market_name_list = list( filter( lambda x: x, market_name_list) )
            market_name_list.append( "выиграют одну карту" )
            market_name_list.sort()
        return market_name_list

    data["name_markets"] = get_market_list()

    if params:

        if not params["num_snapshot"].isdigit():
            return "Bad param", 400

        time_start, time_end = convert_date(params['time'])
        query = db.execute_sql(
            f"SELECT * FROM fixture WHERE m_timestamp > {time_start} \
            AND m_timestamp < {time_end} "
        )

        fixtures = []
        for row in query.fetchall():
            fixtures.append( IFixture(*row[1:]) )


        index = int(params['num_snapshot'])

        for e, fixture in enumerate( fixtures ):
            if index:
                query = db.execute_sql(
                    f"SELECT * FROM market INNER JOIN result ON market.c_id = result.c_id \
                    WHERE m_id = {fixture.m_id} \
                    AND m_snapshot_time < {fixture.m_timestamp - ( (index - 1) * 60) } \
                    AND m_snapshot_time > {fixture.m_timestamp - ( (index - 1) * 60 + 55)}")
            else:
                query = db.execute_sql(
                    f"SELECT * FROM market INNER JOIN result ON market.c_id = result.c_id \
                    WHERE m_id = {fixture.m_id} \
                    AND m_snapshot_time > {fixture.m_timestamp} \
                    AND m_snapshot_time = \
                    ( SELECT m_snapshot_time FROM market WHERE m_id = {fixture.m_id} \
                    ORDER BY id DESC LIMIT 1 )"
                )
            fixture.markets = []

            if not query.rowcount:
                continue

            markets = query.fetchall()
            for market in markets:

                mres = IMarketResult( *market[1:7], *market[9:])
                fixture.markets.append( mres )

        fixtures = list( filter( lambda x : x.markets, fixtures) )

        params['sum_t1'] = int( params['sum_t1'] )
        params['sum_t2'] = int( params['sum_t2'] )
        params['num_snapshot'] = int( params['num_snapshot'] )
        query = get_search( params, fixtures )

        data['result'] = query
        data['params'] = params

    return render_template("filter.html", data = data)


@app.before_request
def before_request():
    if request.endpoint == "filter_page":
        # g.objects = load_objects()
        pass


if __name__ == '__main__':
    PRODUCTION_WORK = True
    if PRODUCTION_WORK:
        serve(app, host='0.0.0.0', port=5000)
    else:
        app.run(port=5000, host='0.0.0.0', debug=True)
