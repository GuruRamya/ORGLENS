#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests


def log(msg, level="INFO"):
    prefix = {"INFO": "ℹ️ ", "OK": "✅ ", "WARN": "⚠️ ", "ERR": "❌ ", "WAIT": "⏳ "}
    print(f"{prefix.get(level, '')} {msg}", flush=True)


def post(base, path, **kwargs):
    r = requests.post(f"{base}{path}", **kwargs)
    r.raise_for_status()
    return r.json()


def get(base, path, **kwargs):
    r = requests.get(f"{base}{path}", **kwargs)
    r.raise_for_status()
    return r.json()


def main():
    parser = argparse.ArgumentParser(description="Seed OrgLens demo organization")
    parser.add_argument("--zip", required=True, help="Path to your ZIP file")
    parser.add_argument("--api", default="http://localhost:8000", help="Backend base URL")
    parser.add_argument("--email", default="demo@orglens.app", help="Demo admin email")
    parser.add_argument("--password", default="DemoOrgLens2024!", help="Demo admin password")
    parser.add_argument("--org-name", default="OrgLens Corp (Demo)", help="Demo org name")
    parser.add_argument("--industry", default="Technology", help="Demo org industry")
    parser.add_argument("--size", type=int, default=40, help="Demo org size estimate")
    parser.add_argument(
        "--mission",
        default="We move fast, value transparency, and put our people first.",
        help="Demo org mission statement",
    )
    parser.add_argument("--out", default="demo_config.json", help="Output config file")
    args = parser.parse_args()

    zip_path = Path(args.zip)
    if not zip_path.exists():
        log(f"ZIP file not found: {zip_path}", "ERR")
        sys.exit(1)

    BASE = args.api.rstrip("/")
    log(f"Targeting API: {BASE}")

    try:
        r = requests.get(f"{BASE}/health", timeout=50)
        r.raise_for_status()
        log("Backend is healthy", "OK")
    except Exception as e:
        log(f"Cannot reach backend: {e}", "ERR")
        sys.exit(1)

    token = None
    log(f"Registering demo user: {args.email}")
    try:
        data = post(BASE, "/api/auth/register", json={
            "email": args.email,
            "password": args.password,
            "full_name": "Demo Admin",
        })
        token = data["access_token"]
        log("Demo user registered", "OK")
    except requests.HTTPError as e:
        if e.response.status_code == 400:
            log("User already exists, logging in…", "WARN")
            data = post(BASE, "/api/auth/token", data={
                "username": args.email,
                "password": args.password,
            })
            token = data["access_token"]
            log("Logged in", "OK")
        else:
            log(f"Auth error: {e}", "ERR")
            sys.exit(1)

    headers = {"Authorization": f"Bearer {token}"}

    log("Creating demo organization…")
    org_id = None

    try:
        orgs = get(BASE, "/api/organizations", headers=headers)
        for org in orgs:
            if org.get("name") == args.org_name:
                org_id = org["id"]
                log(f"Reusing existing demo org: {org_id}", "WARN")
                break
    except Exception:
        pass

    if not org_id:
        org_data = post(BASE, "/api/organizations", headers=headers, json={
            "name": args.org_name,
            "industry": args.industry,
            "size_estimate": args.size,
            "mission_statement": args.mission,
        })
        org_id = org_data["id"]
        log(f"Demo org created: {org_id}", "OK")

    log(f"Uploading ZIP: {zip_path.name} ({zip_path.stat().st_size // 1024} KB)…")
    with open(zip_path, "rb") as f:
        upload_resp = requests.post(
            f"{BASE}/api/upload/zip",
            headers=headers,
            files={"file": (zip_path.name, f, "application/zip")},
            data={"org_id": org_id},
        )
    upload_resp.raise_for_status()
    upload_data = upload_resp.json()
    log(f"Upload complete: {upload_data.get('message', 'success')}", "OK")
    log(f"  Records parsed: {upload_data.get('records_parsed', '?')}")

    log("Triggering analysis…")
    analysis_resp = post(BASE, f"/api/analysis/trigger/{org_id}", headers=headers)
    analysis_id = analysis_resp["analysis_id"]
    log(f"Analysis queued: {analysis_id}", "OK")
    log("Estimated time: 3–8 minutes depending on data size", "WAIT")

    log("Waiting for analysis to complete…", "WAIT")
    max_wait = 60 * 20  
    poll_interval = 10
    elapsed = 0
    final_status = None

    while elapsed < max_wait:
        time.sleep(poll_interval)
        elapsed += poll_interval
        try:
            status_data = get(BASE, f"/api/analysis/status/{analysis_id}", headers=headers)
            status = status_data.get("status", "unknown")
            progress = status_data.get("progress", 0)
            log(f"  [{elapsed:3d}s] status={status} progress={progress}%")

            if status == "completed":
                final_status = "completed"
                log("Analysis complete!", "OK")
                break
            elif status == "failed":
                final_status = "failed"
                log(f"Analysis failed: {status_data.get('message', '')}", "ERR")
                break
        except Exception as e:
            log(f"  Poll error (will retry): {e}", "WARN")

    if final_status != "completed":
        log("Analysis did not complete in time. Check Celery worker logs.", "ERR")
        log(f"You can still set org_id={org_id} / analysis_id={analysis_id} manually and retry.", "WARN")
        final_status = final_status or "pending"

    config = {
        "demo_org_id": org_id,
        "demo_analysis_id": analysis_id,
        "demo_org_name": args.org_name,
        "demo_status": final_status,
        "demo_email": args.email,
        "demo_password": args.password,
        "api_base": BASE,
        "seeded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    with open(args.out, "w") as f:
        json.dump(config, f, indent=2)

    log(f"Config saved to {args.out}", "OK")
    print()
    print("=" * 60)
    print("  NEXT STEPS")
    print("=" * 60)
    print()
    print("Add these to your frontend .env:")
    print()
    print(f"  VITE_DEMO_ORG_ID={org_id}")
    print(f"  VITE_DEMO_ANALYSIS_ID={analysis_id}")
    print()
    print("Then restart your frontend dev server.")
    print()
    print("Recruiters can now visit:  /demo")
    print()


if __name__ == "__main__":
    main()
