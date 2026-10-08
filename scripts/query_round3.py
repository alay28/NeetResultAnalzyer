import csv


CSV_FILE = "round3_allotments.csv"


def normalize(text):
    return " ".join(text.strip().upper().split())


def main():

    print("=" * 100)
    print("ROUND 3 QUERY")
    print("=" * 100)
    print()

    # Get query parameters from user
    min_rank = int(input("Minimum rank: ").strip())
    max_rank = int(input("Maximum rank: ").strip())

    course = input("Course: ").strip()
    candidate_category = input("Candidate category: ").strip()
    allotted_category = input("Allotted category: ").strip()

    print()
    print("=" * 100)

    matches = []

    with open(
        CSV_FILE,
        "r",
        encoding="utf-8-sig"
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            rank = int(row["rank"])

            if rank < min_rank or rank > max_rank:
                continue

            if normalize(row["r3_course"]) != normalize(course):
                continue

            if normalize(row["r3_candidate_category"]) != normalize(
                candidate_category
            ):
                continue

            if normalize(row["r3_allotted_category"]) != normalize(
                allotted_category
            ):
                continue

            matches.append(row)

    print()
    print(f"Rank range: {min_rank} - {max_rank}")
    print(f"Course: {course}")
    print(f"Candidate category: {candidate_category}")
    print(f"Allotted category: {allotted_category}")
    print()
    print(f"Matches found: {len(matches)}")
    print()

    if not matches:
        print("No matching records found.")
        return

    print(
        f"{'Rank':<10}"
        f"{'Quota':<35}"
        f"Institute"
    )

    print("-" * 100)

    for row in matches:

        print(
            f"{row['rank']:<10}"
            f"{row['r3_quota']:<35}"
            f"{row['r3_institute']}"
        )

    print()
    print("=" * 100)


if __name__ == "__main__":
    main()