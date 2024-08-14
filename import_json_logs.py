import os
import argparse
from database import Database


def import_json_logs(log_dir, user_id):
    db = Database()

    for filename in os.listdir(log_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(log_dir, filename)
            print(f"Importing {filename}...")
            try:
                db.import_json(file_path, user_id)
                print(f"Successfully imported {filename}")
            except Exception as e:
                print(f"Error importing {filename}: {str(e)}")

    db.close()
    print("Import completed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import JSON logs into the database")
    parser.add_argument("log_dir", help="Directory containing JSON log files")
    parser.add_argument(
        "user_id", type=int, help="User ID to associate with imported invoices"
    )
    args = parser.parse_args()

    import_json_logs(args.log_dir, args.user_id)
