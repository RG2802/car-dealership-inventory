"""Trusted operator commands; public registration always creates a buyer."""

import argparse
import getpass
import os
from backend.db import connect, initialize
from backend.security import passwords
from backend.schemas import Credentials

DEMO = [
    ("Toyota", "Camry", "Sedan", 3250025, 6),
    ("BMW", "330i", "Sedan", 4590000, 3),
    ("Volvo", "XC60", "SUV", 4875000, 4),
    ("Volkswagen", "Golf", "Hatchback", 2890000, 8),
    ("Hyundai", "Ioniq 5", "Electric", 4195000, 0),
    ("Ford", "Bronco", "SUV", 3999500, 2),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["create-admin", "seed"])
    parser.add_argument("--email")
    args = parser.parse_args()
    path = os.environ.get("DATABASE_PATH", "data/dealership.db")
    initialize(path)
    with connect(path) as db:
        if args.command == "seed":
            if db.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0]:
                raise SystemExit("Seed refused: inventory is not empty")
            db.executemany(
                "INSERT INTO vehicles(make,model,category,price_cents,quantity) VALUES (?,?,?,?,?)",
                DEMO,
            )
            print("Created six fictional demo inventory entries.")
        else:
            email = args.email or input("Admin email: ")
            password = getpass.getpass("Admin password (10–128 characters): ")
            data = Credentials(email=email, password=password)
            # Existing accounts are never silently promoted or overwritten.
            db.execute(
                "INSERT INTO users(email,password_hash,role) VALUES (?,?,'admin')",
                (str(data.email).lower(), passwords.hash(data.password)),
            )
            print("Administrator created.")


if __name__ == "__main__":
    main()
