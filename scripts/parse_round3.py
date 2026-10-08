import pdfplumber
import sys
import re
import csv


if len(sys.argv) != 2:
    print("Usage: python scripts/parse_round3.py <pdf_path>")
    sys.exit(1)


pdf_path = sys.argv[1]


# ------------------------------------------------------------
# R3 columns that are stable
# ------------------------------------------------------------

COLUMNS = {
    "r1_course": (195, 240),
    "r1_remarks": (240, 300),

    "r2_course": (480, 525),
    "r2_remarks": (525, 575),

    "r3_course": (865, 995),
    "r3_allotted_category": (995, 1035),
    "r3_candidate_category": (1035, 1088),
    "r3_option": (1088, 1125),
    "r3_remarks": (1125, 1191),
}


def get_column(x):

    for name, (x_min, x_max) in COLUMNS.items():

        if x_min <= x < x_max:
            return name

    return None


# ------------------------------------------------------------
# Find records on a page
# ------------------------------------------------------------

def extract_page_records(page):

    words = page.extract_words(
        x_tolerance=2,
        y_tolerance=3
    )

    words = sorted(
        words,
        key=lambda w: (w["top"], w["x0"])
    )

    lines = []

    for word in words:

        if not lines:
            lines.append([word])
            continue

        previous_y = lines[-1][0]["top"]

        if abs(word["top"] - previous_y) <= 1.0:
            lines[-1].append(word)
        else:
            lines.append([word])

    records = []
    current_record = None

    for line in lines:

        line = sorted(
            line,
            key=lambda w: w["x0"]
        )

        text = " ".join(
            w["text"]
            for w in line
        )

        # A real rank must be the first word on the line
# and must physically be inside the Rank column.
        match = re.match(r"^(\d+)\s+", text)

        is_rank = (
            match is not None
            and len(line) > 0
            and line[0]["x0"] < 50
        )

        if is_rank:

            if current_record is not None:
                records.append(current_record)

            current_record = {
                "rank": int(match.group(1)),
                "lines": [line]
            }

        elif current_record is not None:

            if text.startswith("Page No."):
                break

            current_record["lines"].append(line)

    if current_record is not None:
        records.append(current_record)

    return records


# ------------------------------------------------------------
# Extract R3 left-side words
# ------------------------------------------------------------

def extract_r3_left_words(record):

    words = []

    for line in record["lines"]:

        for word in line:

            x = word["x0"]

            if 575 <= x < 865:
                words.append(word)

    return sorted(
        words,
        key=lambda w: (w["top"], w["x0"])
    )


# ------------------------------------------------------------
# Reconstruct quota + institute
# ------------------------------------------------------------

def reconstruct_quota_and_institute(record):

    words = extract_r3_left_words(record)

    if not words:
        return "", ""

    text = " ".join(
        word["text"]
        for word in words
    )

    # --------------------------------------------------------
    # DNB Quota
    # --------------------------------------------------------

    if (
    any(word["text"].upper() == "DNB" for word in words)
    and any(word["text"].lower() == "quota" for word in words)
    ):

        quota = "DNB Quota"

        quota_indices = set()

        for i, word in enumerate(words):

            value = word["text"].lower()

            if value == "dnb":
                quota_indices.add(i)

            elif value == "quota":
                quota_indices.add(i)

        institute = " ".join(
            word["text"]
            for i, word in enumerate(words)
            if i not in quota_indices
        ).strip()

        return quota, institute

    # --------------------------------------------------------
    # All India
    # --------------------------------------------------------

    if re.search(
        r"\bAll\s+India\b",
        text,
        re.IGNORECASE
    ):

        quota = "All India"

        quota_indices = set()

        for i, word in enumerate(words):

            if word["text"].lower() == "all":
                quota_indices.add(i)

            elif (
                word["text"].lower() == "india"
                and i > 0
                and i - 1 in quota_indices
            ):
                quota_indices.add(i)

        institute = " ".join(
            word["text"]
            for i, word in enumerate(words)
            if i not in quota_indices
        ).strip()

        return quota, institute

    # --------------------------------------------------------
    # Self-Financed Merit Seat
    #
    # The PDF extraction sometimes puts institute words
    # between "Self-" and "Financed Merit Seat".
    # --------------------------------------------------------

    self_index = None
    financed_index = None
    merit_index = None
    seat_index = None

    for i, word in enumerate(words):

        value = word["text"].lower()

        if self_index is None and value.startswith("self-"):
            self_index = i
            continue

        if self_index is not None and financed_index is None:

            if value == "financed":
                financed_index = i
                continue

        if financed_index is not None and merit_index is None:

            if value == "merit":
                merit_index = i
                continue

        if merit_index is not None and seat_index is None:

            if value == "seat":
                seat_index = i
                break

    if (
        self_index is not None
        and financed_index is not None
        and merit_index is not None
        and seat_index is not None
    ):

        quota = "Self-Financed Merit Seat"

        quota_indices = {
            self_index,
            financed_index,
            merit_index,
            seat_index
        }

        institute = " ".join(
            word["text"]
            for i, word in enumerate(words)
            if i not in quota_indices
        ).strip()

        return quota, institute

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    return "", text.strip()

def extract_round_left_fields(record, quota_min, quota_max, institute_min, institute_max):
    words = []

    for line in record["lines"]:
        for word in line:
            x = word["x0"]

            if quota_min <= x < institute_max:
                words.append(word)

    quota_words = []
    institute_words = []

    for word in words:
        x = word["x0"]

        if quota_min <= x < quota_max:
            quota_words.append(word["text"])

        elif institute_min <= x < institute_max:
            institute_words.append(word["text"])

    quota = " ".join(quota_words).strip()
    institute = " ".join(institute_words).strip()

    return quota, institute
# ------------------------------------------------------------
# Extract complete R3 fields
# ------------------------------------------------------------

def extract_r3_fields(record):

    r1_quota, r1_institute = extract_round_left_fields(
        record,
        40,
        75,
        75,
        200
    )

    r2_quota, r2_institute = extract_round_left_fields(
        record,
        300,
        365,
        365,
        475
    )

    quota, institute = reconstruct_quota_and_institute(record)

    fields = {
    "rank": record["rank"],

    "r1_quota": r1_quota,
    "r1_institute": r1_institute,
    "r1_course": [],
    "r1_remarks": [],

    "r2_quota": r2_quota,
    "r2_institute": r2_institute,
    "r2_course": [],
    "r2_remarks": [],

    "r3_quota": quota,
    "r3_institute": institute,
    "r3_course": [],
    "r3_allotted_category": [],
    "r3_candidate_category": [],
    "r3_option": [],
    "r3_remarks": [],
    }  

    for line in record["lines"]:

        for word in line:

            column = get_column(word["x0"])

            if column is not None:
                fields[column].append(word["text"])

    for key in fields:
        if key in (
            "rank",
            "r1_quota",
            "r1_institute",
            "r2_quota",
            "r2_institute",
            "r3_quota",
            "r3_institute"
        ):
            continue

        fields[key] = " ".join(
            fields[key]
        ).strip()

    return fields


# ------------------------------------------------------------
# Main parser
# ------------------------------------------------------------

def main():

    all_records = []

    print("Opening PDF...")
    print()

    with pdfplumber.open(pdf_path) as pdf:

        total_pages = len(pdf.pages)

        print(f"Total pages: {total_pages}")
        print("Parsing...")

        for page_number, page in enumerate(
            pdf.pages,
            start=1
        ):

            records = extract_page_records(page)

            if not records:
                continue

            for record in records:

                fields = extract_r3_fields(record)

                fields["page_number"] = page_number

                all_records.append(fields)

            if page_number % 100 == 0:

                print(
                    f"Processed page "
                    f"{page_number}/{total_pages} "
                    f"| Records: {len(all_records)}"
                )

    # --------------------------------------------------------
    # Save CSV
    # --------------------------------------------------------

    output_file = "round3_allotments.csv"

    fieldnames = [
    "rank",

    "r1_quota",
    "r1_institute",
    "r1_course",
    "r1_remarks",

    "r2_quota",
    "r2_institute",
    "r2_course",
    "r2_remarks",

    "r3_quota",
    "r3_institute",
    "r3_course",
    "r3_allotted_category",
    "r3_candidate_category",
    "r3_option",
    "r3_remarks",

    "page_number",
]

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(all_records)

    print()
    print("=" * 80)
    print(f"Total records extracted: {len(all_records)}")
    print(f"CSV saved to: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()