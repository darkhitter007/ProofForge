from __future__ import annotations
import argparse
import json
from pathlib import Path
from .case import init_case, ingest, set_case_metadata
from .claims import add_claim
from .build import build_case
from .verify import verify_case
from .exporter import export_case
from .pack import pack_case
from .bundle import verify_bundle

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="proofforge")
    p.add_argument("--workspace", default="cases", help="Case workspace directory")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("init")
    s.add_argument("case_id")
    s.add_argument("--title", required=True)
    s.add_argument("--force", action="store_true", help="Delete and recreate an existing case")

    s = sub.add_parser("demo-reset")
    s.add_argument("case_id", nargs="?", default="DEMO-001")
    s.add_argument("--title", default="Synthetic authorized demonstration")

    s = sub.add_parser("ingest")
    s.add_argument("case_id")
    s.add_argument("source")

    s = sub.add_parser("set-meta")
    s.add_argument("case_id")
    s.add_argument("--authorization", choices=["UNCONFIRMED", "CONFIRMED"])
    s.add_argument("--target")

    s = sub.add_parser("claim-add")
    s.add_argument("case_id")
    s.add_argument("--id", required=True, dest="claim_id")
    s.add_argument("--text", required=True)
    s.add_argument("--evidence", action="append", default=[])
    s.add_argument("--severity", choices=["info", "low", "medium", "high", "critical"], default="medium")

    s = sub.add_parser("build")
    s.add_argument("case_id")
    s.add_argument("--strict", action="store_true")

    s = sub.add_parser("verify")
    s.add_argument("case_id")
    s.add_argument("--json-only", action="store_true")

    s = sub.add_parser("export")
    s.add_argument("case_id")
    s.add_argument("--format", choices=["hackerone", "generic"], default="generic")

    s = sub.add_parser("pack")
    s.add_argument("case_id")

    s = sub.add_parser("verify-bundle")
    s.add_argument("bundle")
    return p

def main() -> None:
    args = parser().parse_args()
    workspace = Path(args.workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    if args.command == "init":
        print(init_case(args.case_id, args.title, workspace, force=args.force))
    elif args.command == "demo-reset":
        print(init_case(args.case_id, args.title, workspace, force=True))
    elif args.command == "ingest":
        print(json.dumps(ingest(args.case_id, Path(args.source), workspace), indent=2))
    elif args.command == "set-meta":
        print(json.dumps(set_case_metadata(
            args.case_id,
            workspace,
            authorization_status=args.authorization,
            target=args.target,
        ), indent=2))
    elif args.command == "claim-add":
        print(json.dumps(add_claim(
            args.case_id,
            workspace,
            claim_id=args.claim_id,
            text=args.text,
            evidence_paths=args.evidence,
            severity=args.severity,
        ), indent=2))
    elif args.command == "build":
        result = build_case(args.case_id, workspace, strict=args.strict)
        if result.get("package_id"):
            print(f'ProofForge package: {result["package_id"]} | root={result["case_root_sha256"]}')
        print(json.dumps(result, indent=2))
        raise SystemExit(1 if result["status"] == "BLOCKED" else 0)
    elif args.command == "verify":
        result = verify_case(args.case_id, workspace)
        if not args.json_only:
            s = result.get("summary", {})
            print(
                f'ProofForge verification: {result["status"]} | '
                f'passed={s.get("passed_checks", 0)} '
                f'failed={s.get("failed_checks", 0)} '
                f'errors={s.get("error_count", len(result.get("errors", [])))} '
                f'package={result.get("package_id")}'
            )
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result["status"] == "PASS" else 1)
    elif args.command == "export":
        print(export_case(args.case_id, workspace, args.format))
    elif args.command == "pack":
        out, identity = pack_case(args.case_id, workspace)
        print(f'{out}\npackage_id={identity["package_id"]}\ncase_root_sha256={identity["case_root_sha256"]}')
    elif args.command == "verify-bundle":
        result = verify_bundle(Path(args.bundle))
        print(f'ProofForge bundle verification: {result["status"]} | case={result.get("case_id")} package={result.get("package_id")}')
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()
