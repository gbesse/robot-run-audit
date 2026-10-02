"""Create a synthetic MCAP recording with a deliberate camera gap."""

import argparse
from pathlib import Path

from mcap.writer import Writer


def main():
    parser = argparse.ArgumentParser(description="Create a synthetic MCAP / Créer un MCAP synthétique / Crear un MCAP sintético")
    parser.add_argument("output")
    args = parser.parse_args()
    with Path(args.output).open("wb") as output:
        writer = Writer(output)
        writer.start()
        schema = writer.register_schema("sample", "jsonschema", b"{}")
        camera = writer.register_channel("/camera", "json", schema)
        joints = writer.register_channel("/joint_states", "json", schema)
        for stamp in (1_000_000_000, 1_100_000_000, 1_500_000_000):
            writer.add_message(camera, stamp, b"{}", stamp)
        for index in range(30):
            stamp = 1_000_000_000 + index * 20_000_000
            writer.add_message(joints, stamp, b"{}", stamp)
        writer.finish()


if __name__ == "__main__":
    main()
