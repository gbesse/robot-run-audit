import tempfile
import unittest
from pathlib import Path
import sqlite3

from mcap.writer import Writer
from robot_run_audit import audit


class AuditTests(unittest.TestCase):
    def test_flags_gap_and_missing_topic(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.mcap"
            with path.open("wb") as output:
                writer = Writer(output)
                writer.start()
                schema = writer.register_schema("sample", "jsonschema", b"{}")
                channel = writer.register_channel("/camera", "json", schema)
                for stamp in (1_000_000_000, 1_100_000_000, 1_500_000_000):
                    writer.add_message(channel, stamp, b"{}", stamp)
                writer.finish()
            report = audit(path, {"topics": {"/camera": {"max_gap_ms": 150}, "/joint_states": {}}}, "fr")
            self.assertEqual(report["status"], "fail")
            self.assertEqual({item["code"] for item in report["findings"]}, {"gap", "missing"})
            self.assertEqual(len(report["source"]["sha256"]), 64)

    def test_clean_recording(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.mcap"
            with path.open("wb") as output:
                writer = Writer(output)
                writer.start()
                schema = writer.register_schema("sample", "jsonschema", b"{}")
                channel = writer.register_channel("/camera", "json", schema)
                for stamp in (1_000_000_000, 1_100_000_000, 1_200_000_000):
                    writer.add_message(channel, stamp, b"{}", stamp)
                writer.finish()
            report = audit(path, {"topics": {"/camera": {"min_hz": 8}}}, "es")
            self.assertEqual(report["status"], "pass")

    def test_rosbag2_sqlite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.db3"
            connection = sqlite3.connect(path)
            connection.executescript("CREATE TABLE topics(id INTEGER, name TEXT); CREATE TABLE messages(topic_id INTEGER, timestamp INTEGER); INSERT INTO topics VALUES(1, '/camera'); INSERT INTO messages VALUES(1, 1000000000), (1, 1100000000), (1, 1200000000);")
            connection.commit()
            connection.close()
            report = audit(path, {"topics": {"/camera": {"min_hz": 8}}})
            self.assertEqual(report["status"], "pass")


if __name__ == "__main__":
    unittest.main()
