"""Upsert the editable Houston resource catalog into Supabase."""

import json
import os
from pathlib import Path

from env_loader import load_env_file
from supabase import create_client


DATA_FILE = Path(__file__).parent / "data" / "houston_food_resources.json"
load_env_file(Path(__file__).parent / ".env.admin")


def main() -> None:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise SystemExit(
            "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY before syncing."
        )

    dataset = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    records = dataset.get("resources")
    if not isinstance(records, list) or not records:
        raise SystemExit(f"No resource records found in {DATA_FILE}.")

    rows = []
    for record in records:
        rows.append({
            "resource_id": record["resource_id"],
            "name": record["name"],
            "resource_type": record["resource_type"],
            "city": record.get("city") or "",
            "state": record.get("state") or "",
            "zip_code": record.get("zip_code"),
            "source_url": record.get("source_url"),
            "last_verified": record.get("last_verified"),
            "updated_at": record.get("updated_at"),
            "payload": record,
        })

    client = create_client(url, key)
    result = (
        client.table("eatwell_resources")
        .upsert(rows, on_conflict="resource_id")
        .execute()
    )
    print(f"Synced {len(result.data)} Houston resource records to Supabase.")


if __name__ == "__main__":
    main()
