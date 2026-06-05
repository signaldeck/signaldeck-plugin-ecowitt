import math

from signaldeck_plugin_main.processors.dummy_data import data
from signaldeck_sdk import DisplayProcessor, DisplayData
from typing import List, Tuple, Any 
from .displaydata import EcowittDisplayData
from signaldeck_sdk import PersistData
import datetime, json
from zoneinfo import ZoneInfo 

SENSOR_TYPES = {
    "WN31": {
     "temperature_c":   {"data_name": "temp{ch}c", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.temperature_c", "convert_from_fahrenheit": "temperature_f"},
     "temperature_f":   {"data_name": "temp{ch}f", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.temperature_f","show": False},
     "dewpoint_c":   { "data_name": "dewpoint{ch}c", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.dewpoint_c", "calc_dewpoint": ("temperature_c", "humidity")},
     "humidity":   {"data_name": "humidity{ch}", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.humidity"},
     "battery":   {"data_name": "batt{ch}", "dtype": "int", "display_name_key": "signaldeck_plugin_ecowitt.battery"}
    },
    "GW3000": {
        "temperature_c":   {"data_name": "tempinc", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.temperature_c", "convert_from_fahrenheit": "temperature_f"},
        "temperature_f":   {"data_name": "tempinf", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.temperature_f","show": False},
        "dewpoint_c":   { "data_name": "dewpointin", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.dewpoint_c", "calc_dewpoint": ("temperature_c", "humidity")},
        "humidity":   {"data_name": "humidityin", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.humidity"},
        "pressure_rel_inhg":   {"data_name": "baromrelin", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.barometer","show": False},
        "pressure_rel_hpa":   {"data_name": "baromrelin_hpa", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.barometer", "convert_from_inhg": "pressure_rel_inhg"}
        },
    "WS90": {
        "temperature_c":   {"data_name": "tempc", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.temperature_c", "convert_from_fahrenheit": "temperature_f"},
        "temperature_f":   {"data_name": "tempf", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.temperature_f","show": False},
        "humidity":   {"data_name": "humidity", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.humidity"},
        "dewpoint_c":   { "data_name": "dewpoint", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.dewpoint_c", "calc_dewpoint": ("temperature_c", "humidity")},
        "uv":   {"data_name": "uv", "dtype": "int", "display_name_key": "signaldeck_plugin_ecowitt.uv"},
        "solarradiation":   {"data_name": "solarradiation", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.solarradiation"},
        "winddir_10m":   {"data_name": "winddir_avg10m", "dtype": "int", "display_name_key": "signaldeck_plugin_ecowitt.winddir_10m"},
        "maxdailygust_mph":   {"data_name": "maxdailygust", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.winddir_10m","show": False},
        "windspeedmph":   {"data_name": "windspeedmph", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.winddir_10m","show": False},
        "windgustmph":   {"data_name": "windgustmph", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.winddir_10m","show": False},
        "maxdailygust_kmh":   {"data_name": "maxdailygust_kmh", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.maxdailygust_kmh", "convert_from_mph_to_kmh": "maxdailygust_mph"},
        "windspeed_kmh":   {"data_name": "windspeed_kmh", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.windspeed_kmh", "convert_from_mph_to_kmh": "windspeedmph"},
        "windgust_kmh":   {"data_name": "windgust_kmh", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.windgust_kmh", "convert_from_mph_to_kmh": "windgustmph"},        
        "rain_rate_inch":   {"data_name": "rrain_piezo", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.rain_rate","show": False},
        "rain_event_inch":   {"data_name": "erain_piezo", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.rain_event","show": False},
        "rain_1hour_inch":   {"data_name": "hrain_piezo", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.rain_1hour","show": False},
        "rain_24h_inch":   {"data_name": "last24hrain_piezo", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.rain_24hour","show": False},
        "rain_day_inch":   {"data_name": "drain_piezo", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.rain_day","show": False},
        "rain_week_inch":   {"data_name": "wrain_piezo", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.rain_week","show": False},
        "rain_month_inch":   {"data_name": "mrain_piezo", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.rain_month","show": False},
        "rain_year_inch":   {"data_name": "yrain_piezo", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.rain_year","show": False},
        "rain_rate":   {"data_name": "rrain_piezo_mm", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.rain_rate", "convert_from_inch_to_mm": "rain_rate_inch"},
        "rain_event":   {"data_name": "erain_piezo_mm", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.rain_event", "convert_from_inch_to_mm": "rain_event_inch"},
        "rain_1hour":   {"data_name": "hrain_piezo_mm", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.rain_1hour", "convert_from_inch_to_mm": "rain_1hour_inch"},
        "rain_24h":   {"data_name": "last24hrain_piezo_mm", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.rain_24hour", "convert_from_inch_to_mm": "rain_24h_inch"},
        "rain_day":   {"data_name": "drain_piezo_mm", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.rain_day", "convert_from_inch_to_mm": "rain_day_inch"},
        "rain_week":   {"data_name": "wrain_piezo_mm", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.rain_week", "convert_from_inch_to_mm": "rain_week_inch"},
        "rain_month":   {"data_name": "mrain_piezo_mm", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.rain_month", "convert_from_inch_to_mm": "rain_month_inch"},
        "rain_year":   {"data_name": "yrain_piezo_mm", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.rain_year", "convert_from_inch_to_mm": "rain_year_inch"},
        "rain_total":   {"data_name": "srain_piezo", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.rain_total"},
        "battery":   {"data_name": "wh90batt", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.battery"},
        "battery_kondensator":   {"data_name": "ws90cap_volt", "dtype": "float", "display_name_key": "signaldeck_plugin_ecowitt.battery"},
    }
    }

def dewpoint_celsius(temp_c: float, humidity: float) -> float:
    a = 17.62
    b = 243.12

    alpha = (a * temp_c) / (b + temp_c) + math.log(humidity / 100.0)
    return round((b * alpha) / (a - alpha),2)

def fahrenheit_to_celsius(temp_f: float) -> float:
    return round((temp_f - 32.0) * 5.0 / 9.0,2)

class EcowittProcessor(PersistData,DisplayProcessor):

    def __init__(self,name,config,ctx,valueProvider,collect_data):
        super().__init__(name,config,ctx,valueProvider,collect_data)
        self.field_name_from_data = {}
        self.int_fields = set()
        self.float_fields = set()
        self.calc_celsius_from_fahrenheit = {}
        self.calc_mpa_from_inhg = {}
        self.calc_inch_to_mm = {}
        self.calc_dewpoint = {}
        self.calc_mph_to_kmh = {}
        self.sensors = {}
        
        for sensor in self.config.get("sensors",[]):
            self.ctx.logger.info(f"Registering sensor: {sensor['name']} with type: {sensor['type']}")
            self.sensors[sensor["name"]] = sensor
            self.sensors[sensor["name"]]["attr_name"] = {}
            self.sensors[sensor["name"]]["attr"] = []
            self.sensors[sensor["name"]]["display_attrs"] = []
            for sensor_name, sensor_field in SENSOR_TYPES.get(sensor["type"],[]).items():
                sensor_field_name = sensor_name
                sensor_attr_name = f"{sensor['name']}_{sensor_field_name}"
                self.sensors[sensor["name"]]["attr_name"][sensor_field_name] = sensor_attr_name
                self.sensors[sensor["name"]]["attr"].append((sensor_attr_name, sensor_field["display_name_key"]))
                if sensor_field.get("show", True):
                    self.sensors[sensor["name"]]["display_attrs"].append((sensor_attr_name, sensor_field["display_name_key"]))
                self.ctx.logger.info(f"Registering sensor field: {sensor_field_name} for sensor: {sensor['name']}")
                setattr(self, sensor_attr_name, None)
                data_name = sensor_field["data_name"].format(ch=sensor.get("channel", 1))
                self.field_name_from_data[data_name] = sensor_attr_name
                if sensor_field["dtype"] == "int":
                    self.int_fields.add(sensor_attr_name)
                elif sensor_field["dtype"] == "float":
                    self.float_fields.add(sensor_attr_name)
                if "convert_from_fahrenheit" in sensor_field:
                    dep_sensor_attr_name = f"{sensor['name']}_{sensor_field["convert_from_fahrenheit"]}"
                    self.calc_celsius_from_fahrenheit[sensor_attr_name] = dep_sensor_attr_name
                if "convert_from_inhg" in sensor_field:
                    dep_sensor_attr_name = f"{sensor['name']}_{sensor_field["convert_from_inhg"]}"
                    self.calc_mpa_from_inhg[sensor_attr_name] = dep_sensor_attr_name
                if "convert_from_inch_to_mm" in sensor_field:
                    dep_sensor_attr_name = f"{sensor['name']}_{sensor_field["convert_from_inch_to_mm"]}"
                    self.calc_inch_to_mm[sensor_attr_name] = dep_sensor_attr_name
                if "convert_from_mph_to_kmh" in sensor_field:
                    dep_sensor_attr_name = f"{sensor['name']}_{sensor_field["convert_from_mph_to_kmh"]}"
                    self.calc_mph_to_kmh[sensor_attr_name] = dep_sensor_attr_name
                if "calc_dewpoint" in sensor_field:
                    dep_sensor_attr_name1 = f"{sensor['name']}_{sensor_field["calc_dewpoint"][0]}"
                    dep_sensor_attr_name2 = f"{sensor['name']}_{sensor_field["calc_dewpoint"][1]}"
                    self.calc_dewpoint[sensor_attr_name] = (dep_sensor_attr_name1, dep_sensor_attr_name2)
        self.ctx.logger.info(f"Field name from data mapping: {self.field_name_from_data}")  
        self.ctx.logger.info(f"Sensors: {self.sensors}") 
        self.ctx.logger.info(f"Calculated fields:")
        self.ctx.logger.info(f"Celsius: {self.calc_celsius_from_fahrenheit}")
        self.ctx.logger.info(f"MPa: {self.calc_mpa_from_inhg}")
        self.ctx.logger.info(f"MPH to KMH: {self.calc_mph_to_kmh}")
        self.ctx.logger.info(f"Inch to MM: {self.calc_inch_to_mm}")
        self.ctx.logger.info(f"Dewpoint: {self.calc_dewpoint}")

    def assureValueSingle(self, value):
        res = value
        if type(res) is list:
            res = res[0]
        return res



    def getDisplayData(self,value,actionHash,**kwargs) -> DisplayData:
        sensor = self.assureValueSingle(value)
        if sensor and sensor in self.sensors:
            return EcowittDisplayData(self.ctx, actionHash).forSensor(sensor,self)
        return EcowittDisplayData(self.ctx, actionHash).forOverview(self).withData(kwargs)



    def getTemplate(self,value):
        sensor = self.assureValueSingle(value)
        if sensor and sensor in self.sensors:
            return f'ecowitt/{self.sensors[sensor]["type"]}.html'
        if sensor == "overview":
            return "ecowitt/overview.html"
        return "ecowitt/ecowitt.html"
    
    def init_current_vals(self,config=None):
        super().init_current_vals(config)
        for sensor in self.sensors.keys():
            self.sensors[sensor]["last_update"] = self.currVal["date"]
        if self.currVal["date"]:
            if "persist" in self.config:
                lastActionDict = {}
                lastActionDict[json.dumps(self.config["persist"][0])] = self.currVal["date"].timestamp()
                self.dataStores[self.config["persist"][0]["type"]]._last_action_time = lastActionDict
    
   
    def processHTTPCall(self,**kwargs):
        self.ctx.logger.debug(f"Processing HTTP call with data: {kwargs}")
        data = {}
        data["date"] = datetime.datetime.now(ZoneInfo(self.config.get("timezone","Europe/Berlin")))
        for key, value in kwargs.items():
            if key in self.field_name_from_data:
                field_name = self.field_name_from_data[key]
                try:
                    value = float(value)
                except ValueError:
                    pass
                data[field_name] = value
                self.ctx.logger.info(f"Updated field {field_name} with value: {value}")
        for field in self.calc_celsius_from_fahrenheit.keys():
            if field not in data and self.calc_celsius_from_fahrenheit[field] in data:
                data[field] = fahrenheit_to_celsius(data[self.calc_celsius_from_fahrenheit[field]])
                self.ctx.logger.info(f"Calculated celsius field {field} with value: {data[field]} from fahrenheit field {self.calc_celsius_from_fahrenheit[field]} with value: {data[self.calc_celsius_from_fahrenheit[field]]}")
        for field in self.calc_mpa_from_inhg.keys():
            if field not in data and self.calc_mpa_from_inhg[field] in data:
                data[field] = round(data[self.calc_mpa_from_inhg[field]] * 33.8639,2)
                self.ctx.logger.info(f"Calculated mpa field {field} with value: {data[field]} from inhg field {self.calc_mpa_from_inhg[field]} with value: {data[self.calc_mpa_from_inhg[field]]}")
        for field in self.calc_dewpoint.keys():
            if field not in data and self.calc_dewpoint[field][0] in data and self.calc_dewpoint[field][1] in data:
                data[field] = dewpoint_celsius(data[self.calc_dewpoint[field][0]], data[self.calc_dewpoint[field][1]])
                self.ctx.logger.info(f"Calculated dewpoint field {field} with value: {data[field]} from temperature field {self.calc_dewpoint[field][0]} with value: {data[self.calc_dewpoint[field][0]]} and humidity field {self.calc_dewpoint[field][1]} with value: {data[self.calc_dewpoint[field][1]]}")
        for field in self.calc_inch_to_mm.keys():
            if field not in data and self.calc_inch_to_mm[field] in data:
                data[field] = round(data[self.calc_inch_to_mm[field]] * 25.4,2)
                self.ctx.logger.info(f"Calculated mm field {field} with value: {data[field]} from inch field {self.calc_inch_to_mm[field]} with value: {data[self.calc_inch_to_mm[field]]}")
        for field in self.calc_mph_to_kmh.keys():
            if field not in data and self.calc_mph_to_kmh[field] in data:
                data[field] = round(data[self.calc_mph_to_kmh[field]] * 1.60934,2)
                self.ctx.logger.info(f"Calculated kmh field {field} with value: {data[field]} from mph field {self.calc_mph_to_kmh[field]} with value: {data[self.calc_mph_to_kmh[field]]}")
        if len(data) > 1:
            # Only save if we have more than just the date
            for sensor in self.sensors.keys():
                if self.sensors[sensor]["attr"][0][0] in data.keys():
                    self.sensors[sensor]["last_update"] = data["date"]
            self.ctx.logger.info(f"Saving data: {data}")
            self.save_data(data)
            for k in data.keys():
                if k == "date":
                    continue
                self.ctx.logger.info(f"Data saved successfully: {k} = {getattr(self, k)}")
            
        return {"status": "OK"}