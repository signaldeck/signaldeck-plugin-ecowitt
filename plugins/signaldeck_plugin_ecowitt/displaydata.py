from signaldeck_sdk import DisplayData


class EcowittDisplayData(DisplayData):

    def forSensor(self,sensor,processor):
        self.sensor_name = sensor
        self.processor = processor
        sensorData = processor.sensors[sensor]
        self.last_seen = sensorData.get("last_update",None)
        self.date_format = processor.config.get("date_format","%Y-%m-%d %H:%M:%S")
        self.display_name = sensorData.get("display_name")
        self.channel = sensorData.get("channel")
        self.attrs = []
        self.attrs_name_keys={}
        for attr in sensorData["display_attrs"]:
            self.attrs.append(attr[0])
            self.attrs_name_keys[attr[0]] = attr[1]
        return self
    
    def forOverview(self,processor):
        self.processor = processor
        self.date_format = processor.config.get("date_format","%Y-%m-%d %H:%M:%S")
        self.mode = "temperature"
        overview_config = processor.config.get("overview",{})
        self.processor_outdoor = processor.sensors[overview_config.get("outdoor")]
        self.processors_indoor = [processor.sensors[sensor] for sensor in overview_config.get("indoor", [])]
        return self

    def getAttrValue(self,attr):
        if hasattr(self.processor, attr):
            return getattr(self.processor, attr)
        return None
    
    def getFieldValue(self,sensor,field):
        if field == "last_seen":
            val = sensor.get("last_update",None)
            if val:
                return val.strftime(self.date_format)
        if field in sensor.get("attr_name",{}):
            attr_name = sensor["attr_name"][field]
            if hasattr(self.processor, attr_name):
                return getattr(self.processor, attr_name)
        return None
    

    def getAttrDisplayName(self,attr):
        return self.ctx.t(self.attrs_name_keys.get(attr,attr))
    

    def getLastSeen(self):
        return self.last_seen.strftime(self.date_format) if self.last_seen else None
    
    def getStatefullFields(self):
        return ["mode"]
    
    def getFieldForMode(self):
        if not hasattr(self, "mode"):
            return "temperature_c"
        if self.mode == "temperature":
            return "temperature_c"
        elif self.mode == "humidity":
            return "humidity"
        elif self.mode == "dewpoint":
            return "dewpoint_c"
        elif self.mode == "last_seen":
            return "last_seen"

    def buttons(self):
        return {
            "mode_temperature": {
                "name": "mode_temperature",
                "text": self.ctx.t("signaldeck_plugin_ecowitt.mode_temperature"),
                "button_active_condition": ("mode", "temperature"),
                "params": {"mode": "temperature"}
            },
            "mode_humidity": {
                "name": "mode_humidity",
                "text": self.ctx.t("signaldeck_plugin_ecowitt.mode_humidity"),
                "button_active_condition": ("mode", "humidity"),
                "params": {"mode": "humidity"}
            },
            "mode_dewpoint": {
                "name": "mode_dewpoint",
                "text": self.ctx.t("signaldeck_plugin_ecowitt.mode_dewpoint"),
                "button_active_condition": ("mode", "dewpoint"),
                "params": {"mode": "dewpoint"}
            },
            "mode_last_seen": {
                "name": "mode_last_seen",
                "text": self.ctx.t("signaldeck_plugin_ecowitt.mode_last_seen"),
                "button_active_condition": ("mode", "last_seen"),
                "params": {"mode": "last_seen"}
            }
        }