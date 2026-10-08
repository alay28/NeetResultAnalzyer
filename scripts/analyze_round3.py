import csv
import re
from collections import Counter, defaultdict


CSV_FILE = "round3_allotments.csv"


def normalize(text):
    return " ".join(text.strip().upper().split())


def extract_state(institute):

    states = [
        "Andhra Pradesh",
        "Arunachal Pradesh",
        "Assam",
        "Bihar",
        "Chhattisgarh",
        "Goa",
        "Gujarat",
        "Haryana",
        "Himachal Pradesh",
        "Jharkhand",
        "Karnataka",
        "Kerala",
        "Madhya Pradesh",
        "Maharashtra",
        "Manipur",
        "Meghalaya",
        "Mizoram",
        "Nagaland",
        "Odisha",
        "Punjab",
        "Rajasthan",
        "Sikkim",
        "Tamil Nadu",
        "Telangana",
        "Tripura",
        "Uttar Pradesh",
        "Uttarakhand",
        "West Bengal",
        "Delhi",
        "Jammu and Kashmir",
        "Puducherry",
        "Chandigarh",
    ]

    text = institute.lower()

    for state in states:
        if re.search(
            r"\b" + re.escape(state.lower()) + r"\b",
            text
        ):
            return state

    return "Unknown"


def main():

    print("=" * 100)
    print("ROUND 3 STATE & INSTITUTE ANALYSIS")
    print("=" * 100)
    print()

    min_rank = int(input("Minimum rank: ").strip())
    max_rank = int(input("Maximum rank: ").strip())

    course = input("Course: ").strip()
    candidate_category = input("Candidate category: ").strip()
    allotted_category = input("Allotted category: ").strip()

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
    print("=" * 100)
    print("FILTER RESULTS")
    print("=" * 100)

    print(f"Rank range: {min_rank} - {max_rank}")
    print(f"Course: {course}")
    print(f"Candidate category: {candidate_category}")
    print(f"Allotted category: {allotted_category}")
    print(f"Matches found: {len(matches)}")

    if not matches:
        print()
        print("No matching records found.")
        return

    # ---------------------------------------------------------
    # STATE ANALYSIS
    # ---------------------------------------------------------

    state_records = defaultdict(list)

    for row in matches:

        state = extract_state(row["r3_institute"])

        state_records[state].append(row)

    print()
    print("=" * 100)
    print("STATE-WISE SUMMARY")
    print("=" * 100)

    print(
        f"{'State':<25}"
        f"{'Seats':<10}"
        f"{'Best Rank':<12}"
        f"{'Worst Rank'}"
    )

    print("-" * 100)

    state_summary = []

    for state, rows in state_records.items():

        ranks = [
            int(row["rank"])
            for row in rows
        ]

        state_summary.append(
            (
                state,
                len(rows),
                min(ranks),
                max(ranks)
            )
        )

    state_summary.sort(
        key=lambda x: x[2]
    )

    for state, seats, best_rank, worst_rank in state_summary:

        print(
            f"{state:<25}"
            f"{seats:<10}"
            f"{best_rank:<12}"
            f"{worst_rank}"
        )

    # ---------------------------------------------------------
    # INSTITUTE ANALYSIS
    # ---------------------------------------------------------

    institute_records = defaultdict(list)

    for row in matches:

        institute = row["r3_institute"]

        institute_records[institute].append(row)

    print()
    print("=" * 100)
    print("INSTITUTE-WISE SUMMARY")
    print("=" * 100)

    print(
        f"{'Seats':<8}"
        f"{'Best Rank':<12}"
        f"Institute"
    )

    print("-" * 100)

    institute_summary = []

    for institute, rows in institute_records.items():

        ranks = [
            int(row["rank"])
            for row in rows
        ]

        institute_summary.append(
            (
                len(rows),
                min(ranks),
                institute
            )
        )

    institute_summary.sort(
        key=lambda x: x[1]
    )

    for seats, best_rank, institute in institute_summary:

        print(
            f"{seats:<8}"
            f"{best_rank:<12}"
            f"{institute}"
        )

    print()
    print("=" * 100)
    print("DONE")
    print("=" * 100)


if __name__ == "__main__":
    main()
