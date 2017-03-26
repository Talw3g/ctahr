
import  time, json
from . import configuration
import rrdtool

class JSONWrapper():

    def __init__(self, app):
        self.app = app
        self.day = 86400
        self.week = self.day * 7

        self.cached_values = {}

    def get_rrd_json(self, period):
        v,ts = self.cached_values.get(period, (None,None))

        if (v is None) or (time.time() - ts > 15.0):
            v = self._get_rrd_json(period)
            self.cached_values[period] = v,time.time()
            return v
        else:
            return v

    def _get_rrd_json(self, period):
        # Initializing min/max
        tint_min = None
        tint_max = None
        text_min = None
        text_max = None
        # Creating list of data dictionnaries
        data = [{'key':'Interior Temperature', 'values':[], 'yAxis':1, 'type':'line'},
            {'key':'Exterior Temperature', 'values':[], 'yAxis':1, 'type':'line'},
            {'key':'Interior Hygrometry', 'values':[], 'disabled':True, 'yAxis': 2,
                'type':'line'},
            {'key':'Exterior Hygrometry', 'values':[], 'disabled':True, 'yAxis': 2,
                'type':'line'},
            {'key':'Fan Status', 'values':[], 'disabled':True, 'yAxis':1, 'type':'line'},
            {'key':'Heater Status', 'values':[], 'disabled':True, 'yAxis':1, 'type':'line'},
            {'key':'Dehum Status', 'values':[], 'disabled':True, 'yAxis':1, 'type':'line'}]

        raw = rrdtool.fetch(configuration.rrdtool_file,'-r',
            '%ds'%max(1,int(period/1500)),'AVERAGE','-s',
            '-%ds'%int(period))

        # Generating the timestamp list from rrd
        x = [1000*i for i in range(*raw[0])]

        # Stocking values from rrd to 'values' lists
        for i in raw[2]:
            if None not in i:
                for j,*rest in enumerate(data):
                    data[j]['values'].append(round(i[j],2))

                # computing min and max for this period:
                if None in (tint_min, tint_max, text_min, text_max):
                    tint_min = round(i[0],1)
                    tint_max = round(i[0],1)
                    text_min = round(i[1],1)
                    text_max = round(i[1],1)
                else:
                    if i[0] < tint_min:
                        tint_min = round(i[0],1)
                    elif i[0] > tint_max:
                        tint_max = round(i[0],1)
                    if i[1] < text_min:
                        text_min = round(i[1],1)
                    elif i[1] > text_max:
                        text_max = round(i[1],1)
            else:
                for j,*rest in enumerate(data):
                    data[j]['values'].append(None)

        for j,*rest in enumerate(data):
            # Zipping timestamp and values into temporary list
            _values = list(zip(x,data[j]['values']))
            data[j]['values'] = []

            # Removing every line containing a None value:
            for k,*rest in enumerate(_values):
                if None not in _values[k]:
                    data[j]['values'].append(_values[k])

            # Decimating to keep approx. 800 points
            resolution = max(1,int(len(data[j]['values'])/800))
            data[j]['values'] = data[j]['values'][::resolution]

        # Appending min/max values
        data = [data, {'tint_min':tint_min, 'tint_max':tint_max,
            'text_min':text_min, 'text_max':text_max}]

        return json.dumps(data)

