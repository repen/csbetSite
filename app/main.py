from flask import Flask, render_template, request, g
import os, json, re, pickle, logging, time
from Model import CSGame
from objbuild import Market, Fixture
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from Globals import WORK_DIR, PRODUCTION_WORK, DATA_DIR
from tools import hash_, listdir_fullpath, get_search
import itertools, gc
from waitress import serve
from cachier import cachier
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger("__DEBUG__")

pattern001 = r"выигра\w+ \d+ раун\w+|ножом|убийство|выигра\w+ две|три карт\w|ACE|pro100"

app = Flask(__name__)

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
    return (datetime.strptime(start, "%Y-%m-%d").timestamp(), datetime.strptime(end, "%Y-%m-%d").timestamp())

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

@timeit
def load_objects(*args, **kwargs):
    index = kwargs.setdefault("index", -1)
    fixtures = []
    l_objs = listdir_fullpath( OBJECT_DIR )
    gc.disable()
    for path in l_objs:
        try:
            with open(path, "rb") as f:
                fixture = pickle.load(f)
            try:
                # fixture._snapshots = [ fixture._snapshots[ index ] ]
                fixture._snapshots = [ fixture._snapshots[ index ] ]
                fixtures.append(fixture)
            except IndexError as ie:
                print("IndexError", ie)
        except Exception as e:
            print("Error", str(e))
    gc.enable()
    return fixtures

@cachier(stale_after=timedelta(seconds=60*60*5))
def load_objects_cache():
    fixtures = load_objects()
    data = {}
    ts = time.time()

    data["name_markets"] = name_markets_prepare( fixtures )
    data["name_markets"] = list( filter(lambda x: not re.search(pattern001, x), data["name_markets"] ) )
    data["teams"] = sorted( set( itertools.chain.from_iterable( [ [x.team01, x.team02] for x in fixtures] ) ) )
    
    te = time.time()
    
    logger.info("Time {}".format(te-ts) )
    return data

@app.route('/')
def index():
    data = {}
    data['fixtures'] = []
    data['hash_objs'] = list( map( lambda x:x.split("/")[-1] , listdir_fullpath(OBJECT_DIR ) ) )

    
    current_time = datetime.now().timestamp()
    date = request.args.get('date', default=False)
    
    if date:
        date = datetime.strptime(date, "%m/%d/%Y").timestamp()
        fixtures = CSGame.select().where( (date < CSGame.m_time) & (CSGame.m_time < date + 87000))
    else:
        fixtures = CSGame.select().where( CSGame.m_time > current_time + 87000 )
    
    for fixture in fixtures:
        m_id = fixture.m_id
        m_team = "{} vs {}".format( fixture.team1, fixture.team2 )
        m_time = datetime.fromtimestamp( fixture.m_time ).strftime("%Y.%m.%d %H:%M")
        data['fixtures'].append( ( m_id, m_team, m_time,  m_id ) )

    return render_template("index.html", data = data)

@app.route('/match/<m_id>')
def match_page(m_id):
    data = {}
    # return render_template("match.html", data = data)
    path_id = os.path.join( OBJECT_DIR, m_id )
    l_objs = listdir_fullpath( OBJECT_DIR )
    if path_id in l_objs:
        try:
            with open(path_id, "rb") as f:
                fixture = pickle.load(f)
            data['name_markets'] = sorted( list( fixture.name_markets ) )
            data['team1'], data['team2'] = fixture.team01, fixture.team02
            data["result"] = fixture.markets[0]
            res_markets = {}
            first = fixture.markets[0]

            for x in first:
                res_markets[x] = first[x].winner
            
            data['markets'] = fixture.markets
            data["result"] = res_markets
            return render_template("match.html", data = data)
        except Exception as e:
            print("Error", str(e))
            return "Error: " + str(e)
    else:
        return "Not path_id " + m_id 

@app.route('/filter')
def filter_page():
    data = {}
    data['result'] = []
    params = request.args.to_dict()
    fixtures = []


    if params:
        index = params['num_snapshot']
        # import pdb;pdb.set_trace()
        fixtures = load_objects(index= (int( index ) + 1) * -1 )

        params['time'] = convert_date( params['time'] )
        params['sum_t1'] = int( params['sum_t1'] )
        params['sum_t2'] = int( params['sum_t2'] )
        params['num_snapshot'] = int( params['num_snapshot'] )
        query = get_search( params, fixtures )
        # import pdb;pdb.set_trace()


        data['result'] = query
        data['params'] = params
    
    fixtures_c = load_objects_cache()
    data["name_markets"] = fixtures_c["name_markets"]
    data["teams"] = fixtures_c["teams"]
    
    return render_template("filter.html", data = data)


@app.before_request
def before_request():
    if request.endpoint == "filter_page":
        # g.objects = load_objects()
        pass


if __name__ == '__main__':

    if PRODUCTION_WORK:
        serve(app, host='0.0.0.0', port=5000)
    else:
        app.run(port=5000, host='0.0.0.0', debug=True)
