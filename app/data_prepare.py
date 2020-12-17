from bs4 import BeautifulSoup
import re, json
from Model import CSGame


class FieldMatchCollectionError( Exception ):
    pass

class MatchMovedError( Exception ):
    pass

class LineBet:
    __slots__ = ["left", "name", "right"]
    def __init__(self, name, l, r):
        self.left  = l
        self.name  = name
        self.right = r

def num_re(text):
    num = re.findall(r'\d', text)
    res = "".join( num )
    assert res
    return res

def quantity_maps(text):
    text = text.strip().lower()
    print("Quantity_maps: ", text)
    return "bo3" == text

def check_result(text):
    pass

def data_filter(html):
    soup = BeautifulSoup(html, "html.parser")
    type_match = soup.select_one(".bm-about .bm-bo.sys-bo")
    print( type_match  )

class Match:
    def __init__(self, *args):
        self.m_id      = args[0]
        self.m_time    = args[1]
        self.snapshots = args[2]
        self.extract_fields( self.snapshots )



        # self.m_team1  = args[2]
        # self.m_team2  = args[3]
        # self.m_result = args[4]
        # self.mapTb2_5 = True
    
    def bet_line_obj(self, line):

        left_value  = line.select_one(".bet-event__button.bet-button_left").text.strip()
        name_event  = line.select_one(".bet-event__text-inside-part").text.strip()
        right_value = line.select_one(".bet-event__button.bet-button_right").text.strip()

        return LineBet(name_event, num_re( left_value ), num_re(right_value))
        # print(num_re( left_value ),  name_event, num_re(right_value),date_timer )

    def bet_state_extract(self, snapshots):
        for snapshot in snapshots[:-1]:
            html = snapshot['data']

            soup = BeautifulSoup(html, "html.parser")
            bet_events  = soup.select(".bet-events__item")
            # print(len(snapshots))
            # print(snapshot, "!!!!")
            
            date_timer  = soup.select_one(".bet-match__additional-info-item_timer")
            if not date_timer:
                raise MatchMovedError("Match moved")
            date_timer = date_timer.text.strip()
            print( snapshot['time'], snapshot['timestamp'], date_timer )

            # for bet_line in bet_events:
            #     self.bet_line_obj( bet_line )
            #     break

            # print( "Events: ",len( bet_events ) )
            
            # break


    def extract_fields(self, snapshots):
        first = snapshots[0]
        html  =  first['data']
        soup = BeautifulSoup(html, "html.parser")
        [ x.extract() for x in soup.select('.bet-team__rank') ]
        self.team01 = soup.select_one(".bet-team__name.sys-t1name").text.strip()
        self.team02 = soup.select_one(".bet-team__name.sys-t2name").text.strip()


        self.bet_state_extract( snapshots )

        for key in self.__dict__:
            if key == "snapshots":
                continue
            print(key, "\t=", self.__dict__[key])
        print("=========================")


        # last  = snapshots[-1]
        # soup2 = BeautifulSoup(last['data'], "html.parser")


        # self.m_result = soup2.select_one(".bm-line1 .bm-result").text.replace(" ", "").strip()

        # mapTb2_5 = soup2.select_one(".bm-bo.sys-bo").text
        # print( mapTb2_5 )
        # self.mapTb2_5 = quantity_maps( mapTb2_5 )


    def check_filter(self, *args, **kwargs):
        [(0,0), 0, ("", ""), 0, 0, 0, ""]

if __name__ == '__main__':
    xz = 0
    # query = CSGame.select().where( CSGame.m_id == "222088" )
    query = CSGame.select()
    result = query.namedtuples()
    matches = []
    for e, res in enumerate( result[:50] ):
        snapshots = json.loads(res.snapshot)
        print(e, res.m_id, res.m_time, res.active, len(snapshots))
        try:
            Match(res.m_id, res.m_time, snapshots)
        except MatchMovedError as e:
            print("Error")
        # except AttributeError:
        #     xz += 1
        #     print("Error")
        #     print("=======================")

        