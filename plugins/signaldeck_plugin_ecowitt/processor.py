import math
import json
from signaldeck_plugin_main.processors.http.http_receiver import HttpReceiver
from signaldeck_sdk import DisplayProcessor, DisplayData
from .displaydata import EcowittDisplayData

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

class EcowittProcessor(HttpReceiver, DisplayProcessor):
    """Ecowitt sensor definitions and derived values on the shared HTTP input."""

    def __init__(self, name, config, ctx, valueProvider, collect_data):
        self.sensors = {}
        self._sensor_fields = set()
        self._latest_fields = {}
        self._derived = []
        # Ecowitt sends partial sensor reports and alternative units.
        mapping = [dict(config.get("timestamp_mapping", {
            "name": "date", "type": "date", "jsonPath": "now"
        }))]
        for sensor in config.get("sensors", []):
            sensor_name = sensor["name"]
            metadata = dict(sensor, attr_name={}, attr=[], display_attrs=[], last_update=None)
            self.sensors[sensor_name] = metadata
            for field, definition in SENSOR_TYPES[sensor["type"]].items():
                target = f"{sensor_name}_{field}"
                metadata["attr_name"][field] = target
                entry = (target, definition["display_name_key"])
                metadata["attr"].append(entry)
                if definition.get("show", True):
                    metadata["display_attrs"].append(entry)
                self._sensor_fields.add(target)
                self._latest_fields[target] = None
                # Preserve the historical Ecowitt numeric representation (float).
                source = definition["data_name"].format(ch=sensor.get("channel", 1))
                mapping.append({
                    "name": target, "type": "float",
                    "jsonPath": "$." + source,
                    "required": False, "ignore_invalid": True,
                })
                conversions = (
                    ("convert_from_fahrenheit", fahrenheit_to_celsius),
                    ("convert_from_inhg", lambda x: round(x * 33.8639, 2)),
                    ("convert_from_inch_to_mm", lambda x: round(x * 25.4, 2)),
                    ("convert_from_mph_to_kmh", lambda x: round(x * 1.60934, 2)),
                )
                for key, function in conversions:
                    if key in definition:
                        self._derived.append((target, (f"{sensor_name}_{definition[key]}",), function))
                if "calc_dewpoint" in definition:
                    deps = tuple(f"{sensor_name}_{d}" for d in definition["calc_dewpoint"])
                    self._derived.append((target, deps, dewpoint_celsius))
        config["mapping"] = mapping
        for endpoint in config.get("export", {}).get("http", []):
            endpoint.setdefault("allow_get", True)
        super().__init__(name, config, ctx, valueProvider, collect_data)

    def enrich_record(self, record):
        # Conversions run before derived fields that depend on converted values.
        for target, dependencies, function in self._derived:
            if target not in record and all(dep in record for dep in dependencies):
                try:
                    value = function(*(record[dep] for dep in dependencies))
                    if math.isfinite(value):
                        record[target] = value
                except (ValueError, ZeroDivisionError, OverflowError):
                    self.logger.warning("Cannot calculate Ecowitt field %s", target)
        return record

    def validate_record(self, record):
        return super().validate_record(record) and bool(self._sensor_fields.intersection(record))

    def makeDataAvailable(self, config=None):
        # Preserve last known values for individual sensors without copying stale
        # fields into the new record or its persistence history.
        for field in self._sensor_fields.intersection(self.currVal or {}):
            value = self.currVal[field]
            if value is not None:
                self._latest_fields[field] = value

    def getValue(self, fieldName):
        with self._record_lock:
            if fieldName in self._sensor_fields:
                return self._latest_fields[fieldName]
            return super().getValue(fieldName)

    def on_record_saved(self, record):
        for sensor in self.sensors.values():
            if sensor["attr"] and sensor["attr"][0][0] in record:
                sensor["last_update"] = record["date"]

    def init_current_vals(self, config=None):
        record = super().init_current_vals(config)
        if record and record.get("date"):
            self.on_record_saved(record)
            cfg = self.config if config is None else config
            for persist in cfg.get("persist", []):
                store = self.dataStores[persist["type"]]
                if not hasattr(store, "_last_action_time"):
                    store._last_action_time = {}
                store._last_action_time[json.dumps(persist)] = record["date"].timestamp()
        return record

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
    
