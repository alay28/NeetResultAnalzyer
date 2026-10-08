import csv


csv_file = "round3_allotments.csv"


with open(
    csv_file,
    "r",
    encoding="utf-8-sig",
    newline=""
) as f:

    reader = csv.DictReader(f)

    rows = list(reader)


print("=" * 80)
print("CSV VALIDATION")
print("=" * 80)

print()
print(f"Total rows: {len(rows)}")

print()
print("Columns:")
print(reader.fieldnames)

print()
print("First row:")
print(rows[0])

print()
print("Rank 6:")
print(next(row for row in rows if row["rank"] == "6"))

print()
print("Rank 10:")
print(next(row for row in rows if row["rank"] == "10"))

print()
print("Rank 26:")
print(next(row for row in rows if row["rank"] == "26"))

print()
print("Rank 230087:")
print(next(row for row in rows if row["rank"] == "230087"))

print()
print("=" * 80)