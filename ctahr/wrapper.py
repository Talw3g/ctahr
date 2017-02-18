
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
            '-%ds'%int(period+86400),'--end','-1d')

        # Generating the timestamp list from rrd
        x = [1000*i for i in range(*raw[0])]

        # Stocking values from rrd to 'values' lists
        for i in raw[2]:
            if i[0] is not None:
                for j,*rest in enumerate(data):
                    data[j]['values'].append(round(float(i[j]),2))

        for j,*rest in enumerate(data):
            # Zipping each values list with timestamp list
            data[j]['values'] = list(zip(x,data[j]['values']))
            # Decimating to keep approx. 1500 points
            resolution = max(1,int(len(data[j]['values'])/1500))
            data[j]['values'] = data[j]['values'][::resolution]

        return json.dumps(data)

