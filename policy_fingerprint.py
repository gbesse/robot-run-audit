"""Fingerprint the resolved components that make a robot policy executable."""

import argparse
import hashlib
import json
from pathlib import Path
import sys


MESSAGES = {
    "fr": {"component": "Composant {component} différent", "controller": "Convention du contrôleur différente", "input": "Entrée invalide", "same": "Empreintes identiques", "different": "{count} différence(s) dans la politique exécutable"},
    "en": {"component": "Component {component} differs", "controller": "Controller convention differs", "input": "Invalid input", "same": "Fingerprints match", "different": "{count} executable-policy difference(s)"},
    "es": {"component": "El componente {component} es distinto", "controller": "La convención del controlador es distinta", "input": "Entrada no válida", "same": "Las huellas coinciden", "different": "{count} diferencia(s) en la política ejecutable"},
}


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def fingerprint(manifest_path, locale="en"):
    if locale not in MESSAGES:
        raise ValueError("locale")
    path = Path(manifest_path)
    raw = path.read_bytes()
    manifest = json.loads(raw.decode("utf-8"))
    if not isinstance(manifest, dict) or set(manifest) != {"files", "controller"}:
        raise ValueError("manifest")
    files = manifest["files"]
    if not isinstance(files, dict) or not {"weights", "normalization"} <= set(files):
        raise ValueError("files")
    if any(not isinstance(role, str) or not role or not isinstance(name, str) or not name for role, name in files.items()):
        raise ValueError("file role/path")
    controller = manifest["controller"]
    if not isinstance(controller, dict) or set(controller) != {"name", "version", "frame", "units"} or any(not isinstance(controller[key], str) or not controller[key] for key in ("name", "version", "frame")) or not isinstance(controller["units"], dict) or not controller["units"]:
        raise ValueError("controller")
    if any(not isinstance(key, str) or not key or not isinstance(value, str) or not value for key, value in controller["units"].items()):
        raise ValueError("controller units")
    components = {}
    for role, name in sorted(files.items()):
        file_path = path.parent / name
        data = file_path.read_bytes()
        components[role] = {"path": str(file_path), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    identity = {"components": {role: item["sha256"] for role, item in components.items()}, "controller": controller}
    digest = hashlib.sha256(_canonical(identity)).hexdigest()
    return {"format": "robot-policy-fingerprint/v1", "locale": locale, "status": "pass", "fingerprint": digest, "manifest": {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest()}, "components": components, "controller": controller}


def compare(first, second, locale="en"):
    left = fingerprint(first, locale)
    right = fingerprint(second, locale)
    findings = []
    for role in sorted(set(left["components"]) | set(right["components"])):
        if left["components"].get(role, {}).get("sha256") != right["components"].get(role, {}).get("sha256"):
            findings.append({"code": "component", "component": role, "message": MESSAGES[locale]["component"].format(component=role)})
    if left["controller"] != right["controller"]:
        findings.append({"code": "controller", "message": MESSAGES[locale]["controller"]})
    return {"format": "robot-policy-fingerprint/v1", "locale": locale, "status": "fail" if findings else "pass", "summary": MESSAGES[locale]["different"].format(count=len(findings)) if findings else MESSAGES[locale]["same"], "first": left, "second": right, "findings": findings}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Policy identity / Identité de politique / Identidad de política")
    parser.add_argument("action", choices=("inspect", "compare"))
    parser.add_argument("first")
    parser.add_argument("second", nargs="?")
    parser.add_argument("--locale", choices=MESSAGES, default="en")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        if args.action == "inspect" and args.second:
            raise ValueError("second manifest")
        if args.action == "compare" and not args.second:
            raise ValueError("second manifest required")
        report = fingerprint(args.first, args.locale) if args.action == "inspect" else compare(args.first, args.second, args.locale)
    except (OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        print(f"{MESSAGES[args.locale]['input']}: {exc if args.locale == 'en' else type(exc).__name__}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
