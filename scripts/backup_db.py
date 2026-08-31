import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import boto3
import dj_database_url
from botocore.config import Config
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
BACKUP_PREFIX = "db-backups/"
BUCKET_RETENTION = 14
LOCAL_DIR = Path("/srv/django/db-backups")
LOCAL_RETENTION = 7

load_dotenv(BASE_DIR / ".env")

ENDPOINT = os.environ.get("AWS_S3_ENDPOINT_URL") or (
    f"https://{os.environ['OCI_NAMESPACE']}.compat.objectstorage."
    f"{os.environ['OCI_REGION']}.oraclecloud.com"
)
ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID") or os.environ["OCI_ACCESS_KEY"]
SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY") or os.environ["OCI_SECRET_KEY"]
BUCKET = os.environ.get("AWS_STORAGE_BUCKET_NAME") or os.environ["OCI_BUCKET_NAME"]


def main():
    db = dj_database_url.parse(os.environ["DATABASE_URL"])
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    filename = f"jobless-{stamp}.dump"

    with tempfile.TemporaryDirectory() as tmp:
        dump_path = os.path.join(tmp, filename)
        env = os.environ.copy()
        env["PGPASSWORD"] = db["PASSWORD"]
        subprocess.run(
            [
                "pg_dump",
                "-Fc",
                "-h", db["HOST"] or "127.0.0.1",
                "-p", str(db["PORT"] or 5432),
                "-U", db["USER"],
                "-d", db["NAME"],
                "-f", dump_path,
            ],
            env=env,
            check=True,
        )

        LOCAL_DIR.mkdir(parents=True, exist_ok=True)
        local_path = LOCAL_DIR / filename
        local_path.write_bytes(Path(dump_path).read_bytes())

        s3 = boto3.client(
            "s3",
            endpoint_url=ENDPOINT,
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=os.environ.get("OCI_REGION", "uk-london-1"),
            config=Config(
                s3={"addressing_style": "path"},
                request_checksum_calculation="when_required",
                response_checksum_validation="when_required",
            ),
        )
        s3.upload_file(dump_path, BUCKET, BACKUP_PREFIX + filename)
        size = os.path.getsize(dump_path)

    paginator = s3.get_paginator("list_objects_v2")
    objects = []
    for page in paginator.paginate(Bucket=BUCKET, Prefix=BACKUP_PREFIX):
        objects.extend(page.get("Contents", []))
    objects.sort(key=lambda o: o["LastModified"])
    for obj in objects[:-BUCKET_RETENTION]:
        s3.delete_object(Bucket=BUCKET, Key=obj["Key"])

    local_backups = sorted(LOCAL_DIR.glob("jobless-*.dump"))
    for old in local_backups[:-LOCAL_RETENTION]:
        old.unlink()

    print(f"{datetime.now(timezone.utc).isoformat()} backup OK: {filename} ({size} bytes)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{datetime.now(timezone.utc).isoformat()} backup FAILED: {e}", file=sys.stderr)
        sys.exit(1)
