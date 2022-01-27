import pandas as pd
import requests
import json
import datetime
from dateutil.parser import parse
import numpy as np
import time
# def get_config(file="local.ini", sec="DEFAULT"):
#   """Reads a section of a configpareser INI file"""
#   import configparser
#   config = configparser.ConfigParser()
#   config.read(file)
#   section = config[sec]
#   out = {}
#   for i in section.items():
#     out[i[0]] = i[1]
#   return out


def unix_time_millis(dt):
  return (dt - epoch).total_seconds() * 1000

epoch = datetime.datetime.utcfromtimestamp(0)
class TB:
    """
    Reads device data 
    TB(config_file='local.ini',device_name='DEFAULT')
    config_file: Initialization file which cointains sections, each section is a device
                 in ThingsBoard, so each one has a token, device_id, tenant, password, host and port.
                 By default, TB class looks for local.ini and section to DEFAULT
    section: By default DEFAULT is used and is used to specify the device

    """
    def __init__(self,config_file='local.ini',device_name='DEFAULT'):
        """
        
        """
        import pandas as pd
        import requests
        import json
        from dateutil.parser import parse
        import configparser
        config = configparser.ConfigParser()
        config.read(config_file)
        section = config[device_name]
        out = {}
        for i in section.items():
            out[i[0]] = i[1]
        self.init = out
        auth_url = "http://{}:{}/api/auth/login".format(self.init["host"], self.init["port"])
        data = {"username": self.init["tenant"], "password": self.init["password"]}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.post(auth_url, data=json.dumps(data), headers=headers)
        self.jwt_token = json.loads(r.text)['token']
        timeseries = "http://{}:{}/api/plugins/telemetry/DEVICE/{}/keys/timeseries".format(self.init["host"], self.init["port"], self.init["device_id"])
        headers = {"Content-Type":"application/json", "X-Authorization": "Bearer {}".format(self.jwt_token)}
        key = requests.get(timeseries, headers=headers)
        self.key = list(key.text)
        print(key.text)
        

        epoch = datetime.datetime.utcfromtimestamp(0)
        
#         return self.key

    def unix_time_millis(dt):
      return (dt - epoch).total_seconds() * 1000
    
    def request(self):
        auth_url = "http://{}:{}/api/auth/login".format(self.init["host"], self.init["port"])
        data = {"username": self.init["tenant"], "password": self.init["password"]}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.post(auth_url, data=json.dumps(data), headers=headers)
        self.jwt_token = json.loads(r.text)['token']
        timeseries = "http://{}:{}/api/plugins/telemetry/DEVICE/{}/keys/timeseries".format(self.init["host"], self.init["port"], self.init["device_id"])
        headers = {"Content-Type":"application/json", "X-Authorization": "Bearer {}".format(self.jwt_token)}
        keys = requests.get(timeseries, headers=headers)
        self.keys = list(keys.text)
        print(keys.text)
    def get_df(self,key="NONE",
               start_datetime=parse('2015-01-01'),
               end_datetime  =datetime.datetime.now(),
               Lat=0):
        if type(start_datetime) == str:
            start_datetime = parse(start_datetime)
        
        if type(end_datetime) == str:
            end_datetime = parse(end_datetime)
        auth_url = "http://{}:{}/api/auth/login".format(self.init["host"], self.init["port"])
        data = {"username": self.init["tenant"], "password": self.init["password"]}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        r = requests.post(auth_url, data=json.dumps(data), headers=headers)
        self.jwt_token = json.loads(r.text)['token']
        timeseries = "http://{}:{}/api/plugins/telemetry/DEVICE/{}/keys/timeseries".format(self.init["host"], self.init["port"], self.init["device_id"])
        headers = {"Content-Type":"application/json", "X-Authorization": "Bearer {}".format(self.jwt_token)}
        keys = requests.get(timeseries, headers=headers)
        
        self.key = key
        start_m = int(unix_time_millis(start_datetime))
        end_m   = int(unix_time_millis(end_datetime))
        interval= 20000
        limit   = 10000000
        agg     = "NONE"
        timeseries = "http://{}:{}/api/plugins/telemetry/DEVICE/{}/values/timeseries?keys={}&startTs={}&endTs={}&interval={}&limit={}&agg={}".format(self.init["host"],
                                                                                                                                                     self.init["port"], 
                                                                                                                                                     self.init["device_id"], 
                                                                                                                                                     self.key, 
                                                                                                                                                     start_m, 
                                                                                                                                                     end_m,
                                                                                                                                                     interval,
                                                                                                                                                     limit,
                                                                                                                                                     agg)    
        
#         print(timeseries)
        telemetry = requests.get(timeseries, headers=headers)
#         time.sleep(10)
        datos = pd.read_json(telemetry.text, orient=None)
#         print(datos)
        df = pd.DataFrame([i for i in datos[key]])
        df.ts = pd.to_datetime(df.ts,unit='ms')
        df.set_index('ts',inplace=True)
        df.columns = [key]
        for i,valor in enumerate(df[key]):
            try:
                df[key].iloc[i] = float(valor)
            except:
                df[key].iloc[i] = np.nan
        df[key] = df[key].astype("float64")

        #df[key] = pd.to_numeric(df[key])
#         df = df.resample("60S").pad()
        df.dropna(inplace=True)
        
        self.datos = df
        return df

        