import sqlite3
import datetime
from pathlib import Path
from src.database.db_manager import DBManager


def test_db_manager_pragmas_and_init(tmp_path):
    db_file = tmp_path / "test_perf.db"
    dbm = DBManager(str(db_file))

    try:
        journal_mode = dbm.get_pragma("journal_mode")
        assert journal_mode.lower() == "wal"

        synchronous = dbm.get_pragma("synchronous")
        assert synchronous in ("1", "NORMAL")

        cache_size = dbm.get_pragma("cache_size")
        assert int(cache_size) < 0

        temp_store = dbm.get_pragma("temp_store")
        assert temp_store in ("2", "MEMORY")

        dbm.init_tables()
        assert dbm.count_images() == 0
    finally:
        dbm.close()


def test_db_manager_batch_operations(tmp_path):
    db_file = tmp_path / "batch.db"
    dbm = DBManager(str(db_file))

    try:
        dbm.init_tables()

        now = datetime.datetime.now()
        batch_data = [
            {
                "file_path": f"/photos/img_{i}.jpg",
                "file_name": f"img_{i}.jpg",
                "file_size": 1024 * i,
                "format": "JPEG",
                "width": 1920,
                "height": 1080,
                "megapixels": 2.07,
                "datetime": now,
                "camera_make": "Canon",
                "camera_model": "EOS",
                "md5_hash": f"hash_{i}",
            }
            for i in range(1, 11)
        ]

        inserted = dbm.insert_images_batch(batch_data)
        assert inserted == 10
        assert dbm.count_images() == 10

        updates = [
            {
                "file_path": f"/photos/img_{i}_updated.jpg",
                "file_name": f"img_{i}_updated.jpg",
                "file_size": 2048 * i,
                "format": "PNG",
                "width": 3840,
                "height": 2160,
                "megapixels": 8.29,
                "datetime": now,
                "camera_make": "Sony",
                "camera_model": "A7",
                "md5_hash": f"hash_{i}",
            }
            for i in range(1, 6)
        ]

        updated = dbm.update_images_batch(updates)
        assert updated == 5

        row = dbm.get_by_md5("hash_1")
        assert row is not None
        assert row["file_name"] == "img_1_updated.jpg"
        assert row["camera_make"] == "Sony"

        unmodified = dbm.get_by_md5("hash_10")
        assert unmodified is not None
        assert unmodified["file_name"] == "img_10.jpg"
        assert unmodified["camera_make"] == "Canon"

        page1 = dbm.get_images(page=1, page_size=5)
        assert len(page1) == 5
        page2 = dbm.get_images(page=2, page_size=5)
        assert len(page2) == 5
    finally:
        dbm.close()


def test_db_manager_single_insert_and_update(tmp_path):
    db_file = tmp_path / "single.db"
    dbm = DBManager(str(db_file))

    try:
        dbm.init_tables()
        meta = {
            "file_path": "/photos/pic.jpg",
            "file_name": "pic.jpg",
            "file_size": 500,
            "format": "JPEG",
            "width": 800,
            "height": 600,
            "megapixels": 0.48,
            "datetime": "2024-01-01T12:00:00",
            "camera_make": "Nikon",
            "camera_model": "D850",
        }
        dbm.insert_image(meta, "md5_single")
        assert dbm.count_images() == 1

        dbm.update_image_by_md5(
            "md5_single", {**meta, "camera_make": "Nikon Updated"}
        )
        row = dbm.get_by_md5("md5_single")
        assert row["camera_make"] == "Nikon Updated"
    finally:
        dbm.close()


def test_db_manager_backup_wal_consistency(tmp_path):
    db_file = tmp_path / "original.db"
    dbm = DBManager(str(db_file))

    try:
        dbm.init_tables()
        dbm.insert_image({"file_path": "/p1.jpg", "file_name": "p1.jpg"}, "hash1")

        backup_dir = tmp_path / "backups"
        backup_path = dbm.backup(str(backup_dir))

        assert backup_path.exists()

        check_conn = sqlite3.connect(str(backup_path))
        cur = check_conn.execute("SELECT COUNT(*) FROM images")
        count = cur.fetchone()[0]
        check_conn.close()

        assert count == 1
    finally:
        dbm.close()
