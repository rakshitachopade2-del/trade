import unittest

from fastapi.testclient import TestClient

from backend.app.main import app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.context = TestClient(app)
        self.client = self.context.__enter__()

    def tearDown(self):
        self.context.__exit__(None, None, None)

    def test_health_and_provenance(self):
        self.assertEqual(self.client.get("/api/health").json(),
                         {"status": "ok", "mode": "synthetic_demo", "orders_enabled": False})
        demo = self.client.get("/api/demo").json()
        self.assertIn("Synthetic", demo["label"])
        response = self.client.get("/api/replay", params={"as_of": demo["default_as_of"]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["mode"], "synthetic_demo")
        self.assertEqual(response.json()["summary"]["qualified"], 1)

    def test_naive_malformed_and_missing_asof_rejected(self):
        for value in ("2026-10-30T09:35:00", "not-a-time", "", "0001-01-01T00:00:00+14:00",
                      "9999-12-31T23:59:59-12:00"):
            with self.subTest(value=value):
                self.assertEqual(self.client.get("/api/replay", params={"as_of": value}).status_code, 422)
        self.assertEqual(self.client.get("/api/replay").status_code, 422)

    def test_replay_times_have_expected_evidence_transition(self):
        times = self.client.get("/api/demo").json()["replay_times"]
        reports = [self.client.get("/api/replay", params={"as_of": timestamp}).json() for timestamp in times]
        self.assertEqual([report["summary"]["qualified"] for report in reports], [0, 1, 1])
        beta = [next(item for item in report["candidates"] if item["symbol"] == "DEMO_BETA") for report in reports]
        self.assertEqual([item["fundamentals_status"] for item in beta], ["unknown", "unknown", "available"])


if __name__ == "__main__":
    unittest.main()
