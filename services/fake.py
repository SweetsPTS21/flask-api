import csv
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

# Sample data
products = ["6541b60ac5119cad40d2b8a8", "650fa6d68777e3057833a455", "6541b411c5119cad40d2b890",
            "6541b729c5119cad40d2b8b4", "6541b2e7c5119cad40d2b884", "6541b2e7c5119cad40d2b720",
            "6541b2e7c5119cad40d2d413", "6541b2e7c5119cad40d2b8a0", "6541b2e7c5119cad40d2h624",
            "6541b2e7c5119cad40d2g512", "6541b2e7c5119cad40d2b8a1", "6541b2e7c5119cad40d2b8a2"]
users = ["64e9839b01a17287f86b9c8f", "654eddeb8b50cc2f30842d1a", "6550a740ea03570028ea3b96",
         "6550a740ea03570028ea3b97", "6550a740ea03570028ea3b98",]

# Generate fake data
fake_data = []
for _ in range(40):
    record = {
        "_id": fake.uuid4(),
        "rating": round(random.uniform(1.0, 5.0), 1),
        "product": random.choice(products),
        "user": random.choice(users),
        "createdAt": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d %H:%M:%S.%f"),
        "__v": 0
    }
    fake_data.append(record)

# Export to CSV file
csv_file_path = "../src/data/fake_data.csv"
fields = ["_id", "rating", "product", "user", "createdAt", "__v"]

with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fields)

    # Write header
    writer.writeheader()

    # Write data
    writer.writerows(fake_data)

print(f"Fake data exported to {csv_file_path}")
