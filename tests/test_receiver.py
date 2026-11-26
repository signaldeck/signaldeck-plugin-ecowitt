import logging
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

from signaldeck_sdk import ValueProvider
from signaldeck_sdk.context import DateProvider
from signaldeck_sdk.value_provider import HttpRequestError
from signaldeck_plugin_main.processors.http.http_receiver import HttpReceiver
from signaldeck_plugin_ecowitt.processor import EcowittProcessor


def config():
    return {
        "sensors": [
            {"name": "room", "type": "WN31", "channel": 2},
            {"name": "garden", "type": "WS90"},
        ],
        "cacheSize": 10,
        "export": {
            "http": [{"name": "temperature", "values": {}}],
            "values": [{"temp": "room_temperature_c"}],
        },
    }


class ReceiverTests(unittest.TestCase):
    def make(self, cfg=None, collect=True):
        vp = ValueProvider()
        ctx = SimpleNamespace(date=DateProvider(), logger=logging.getLogger(__name__))
        p = EcowittProcessor("weather", cfg or config(), ctx, vp, collect)
        return vp, p

    def test_partial_reports_and_derived_values(self):
        vp, p = self.make()
        self.assertIsInstance(p, HttpReceiver)
        self.assertIsNone(p.init_current_vals())
        self.assertIsNone(vp.getValue("temp"))
        self.assertTrue(vp.dispatchHttp("temperature", "GET", {"temp2f": "68", "humidity2": "50"})["accepted"])
        self.assertEqual(vp.getValue("temp"), 20)
        self.assertAlmostEqual(p.getValue("room_dewpoint_c"), 9.26, places=1)
        self.assertTrue(vp.dispatchHttp("temperature", "POST", {"tempf": "50", "windspeedmph": "10", "rrain_piezo": "1"})["accepted"])
        self.assertEqual(p.getValue("garden_temperature_c"), 10)
        self.assertEqual(p.getValue("garden_windspeed_kmh"), 16.09)
        self.assertEqual(p.getValue("garden_rain_rate"), 25.4)
        self.assertEqual(vp.getValue("temp"), 20)
        self.assertNotIn("room_temperature_c", p.memory["weather"][-1])
        self.assertIsNotNone(p.sensors["room"]["last_update"])
        self.assertFalse(p.processHTTPCall(temp2f="--")["accepted"])
        self.assertEqual(len(p.memory["weather"]), 2)
        self.assertEqual(p.getDisplayData("room", "hash").getAttrValue("room_temperature_c"), 20)

    def test_source_timestamp_and_persistence(self):
        cfg = config()
        cfg["timestamp_mapping"] = {"name": "date", "type": "date", "jsonPath": "$.dateutc"}
        cfg["persist"] = [{"type": "db", "date_field": "date", "fields": [
            {"name": "date", "dtype": "date"},
            {"name": "room_temperature_c", "dtype": "float"},
        ]}]
        _, p = self.make(cfg)
        store = Mock()
        store.get_current_vals.return_value = None
        store.should_save.return_value = True
        store.use_previous_value.return_value = False
        p.registerDataStores({"db": store})
        self.assertIsNone(p.init_current_vals())
        self.assertTrue(p.processHTTPCall(dateutc="2026-01-01T10:00:00Z", temp2f="68")["accepted"])
        self.assertEqual(store.save.call_args.args[1], {
            "date": datetime(2026, 1, 1, 10, tzinfo=timezone.utc), "room_temperature_c": 20,
        })
        self.assertFalse(p.processHTTPCall(dateutc="2026-01-01T10:00:00Z", temp2f="69")["accepted"])
        with self.assertRaises(HttpRequestError):
            p.processHTTPCall(temp2f="68")

    def test_disabled_collection(self):
        _, p = self.make(collect=False)
        with self.assertRaises(HttpRequestError):
            p.processHTTPCall(temp2f="68")
