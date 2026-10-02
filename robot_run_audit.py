"""Read-only checks for MCAP robot recordings."""

import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

from mcap.reader import make_reader


MESSAGES = {
    "fr": {
        "missing": "Sujet attendu absent : {topic}",
        "empty": "Sujet sans message : {topic}",
        "gap": "Intervalle de {gap_ms:.1f} ms sur {topic}, limite {limit_ms:.1f} ms",
        "rate": "Fréquence de {rate:.2f} Hz sur {topic}, minimum {minimum:.2f} Hz",
        "insufficient": "Pas assez de messages pour mesurer la fréquence de {topic}",
        "bad_config": "Configuration invalide : {detail}",
        "bad_file": "Enregistrement illisible : {detail}",
        "summary": "{count} anomalie(s) sur {topics} sujet(s)",
    },
    "en": {
        "missing": "Expected topic missing: {topic}",
        "empty": "Topic has no messages: {topic}",
        "gap": "{gap_ms:.1f} ms gap on {topic}; limit {limit_ms:.1f} ms",
        "rate": "{rate:.2f} Hz on {topic}; minimum {minimum:.2f} Hz",
        "insufficient": "Not enough messages to measure the rate of {topic}",
        "bad_config": "Invalid configuration: {detail}",
        "bad_file": "Unreadable recording: {detail}",
        "summary": "{count} finding(s) across {topics} topic(s)",
    },
    "es": {
        "missing": "Falta el tema esperado: {topic}",
        "empty": "Tema sin mensajes: {topic}",
        "gap": "Intervalo de {gap_ms:.1f} ms en {topic}; límite {limit_ms:.1f} ms",
        "rate": "Frecuencia de {rate:.2f} Hz en {topic}; mínimo {minimum:.2f} Hz",
        "insufficient": "No hay suficientes mensajes para medir la frecuencia de {topic}",
        "bad_config": "Configuración no válida: {detail}",
        "bad_file": "Grabación ilegible: {detail}",
        "summary": "{count} anomalía(s) en {topics} tema(s)",
    },
}


def _finding(locale, code, topic, **details):
    return {
        "code": code,
        "topic": topic,
        "details": details,
        "message": MESSAGES[locale][code].format(topic=topic, **details),
    }


def validate_config(config):
    if not isinstance(config, dict) or not isinstance(config.get("topics"), dict):
        raise ValueError("topics must be an object")
    for topic, rule in config["topics"].items():
        if not isinstance(topic, str) or not topic.startswith("/") or not isinstance(rule, dict):
            raise ValueError("each topic must be an absolute name with an object of rules")
        for key in ("min_hz", "max_gap_ms"):
            if key in rule and (not isinstance(rule[key], (int, float)) or isinstance(rule[key], bool) or rule[key] <= 0):
                raise ValueError(f"{topic}.{key} must be a positive number")


def observations(path):
    if path.suffix == ".db3":
        connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
        try:
            rows = connection.execute("SELECT topics.name, messages.timestamp FROM messages JOIN topics ON topics.id = messages.topic_id ORDER BY messages.timestamp")
            yield from rows
        finally:
            connection.close()
    elif path.suffix == ".mcap":
        with path.open("rb") as source:
            reader = make_reader(source, validate_crcs=True)
            for _, channel, message in reader.iter_messages(log_time_order=True):
                yield channel.topic, message.log_time
    else:
        raise ValueError("supported extensions: .mcap, .db3")


def audit(path, config, locale="en"):
    validate_config(config)
    path = Path(path)
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    streams = {}
    for topic, stamp in observations(path):
        item = streams.setdefault(topic, {"count": 0, "first_ns": None, "last_ns": None, "max_gap_ms": 0.0})
        if item["last_ns"] is not None:
            item["max_gap_ms"] = max(item["max_gap_ms"], (stamp - item["last_ns"]) / 1_000_000)
        item["count"] += 1
        item["first_ns"] = stamp if item["first_ns"] is None else item["first_ns"]
        item["last_ns"] = stamp
    findings = []
    for topic, rule in config["topics"].items():
        stream = streams.get(topic)
        if stream is None:
            findings.append(_finding(locale, "missing", topic))
            continue
        if stream["count"] == 0:
            findings.append(_finding(locale, "empty", topic))
            continue
        duration = (stream["last_ns"] - stream["first_ns"]) / 1_000_000_000
        stream["observed_hz"] = (stream["count"] - 1) / duration if duration > 0 else None
        if "max_gap_ms" in rule and stream["max_gap_ms"] > rule["max_gap_ms"]:
            findings.append(_finding(locale, "gap", topic, gap_ms=stream["max_gap_ms"], limit_ms=rule["max_gap_ms"]))
        if "min_hz" in rule:
            if stream["observed_hz"] is None:
                findings.append(_finding(locale, "insufficient", topic))
            elif stream["observed_hz"] < rule["min_hz"]:
                findings.append(_finding(locale, "rate", topic, rate=stream["observed_hz"], minimum=rule["min_hz"]))
    return {
        "format": "robot-run-audit/v1",
        "source": {"path": str(path), "sha256": digest.hexdigest(), "bytes": path.stat().st_size},
        "locale": locale,
        "status": "pass" if not findings else "fail",
        "summary": MESSAGES[locale]["summary"].format(count=len(findings), topics=len(streams)),
        "streams": streams,
        "findings": findings,
        "limits": {
            "fr": ["Le contenu des messages, la cohérence TF, l’étalonnage des capteurs et la sûreté ne sont pas vérifiés."],
            "en": ["Message payloads, TF consistency, sensor calibration and safety are not verified."],
            "es": ["No se verifican el contenido de los mensajes, la coherencia TF, la calibración de sensores ni la seguridad."],
        }[locale],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Audit an MCAP robot recording / Auditer un enregistrement MCAP / Auditar una grabación MCAP")
    parser.add_argument("recording")
    parser.add_argument("config")
    parser.add_argument("--locale", choices=MESSAGES, default="en")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
        report = audit(args.recording, config, args.locale)
    except ValueError as exc:
        print(MESSAGES[args.locale]["bad_config"].format(detail=exc), file=sys.stderr)
        return 2
    except Exception as exc:
        print(MESSAGES[args.locale]["bad_file"].format(detail=exc), file=sys.stderr)
        return 2
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
