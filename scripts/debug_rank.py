import pdfplumber
import sys
import re
import csv

if len(sys.argv) != 2:
    print("Usage: python scripts/parse_round3.py <pdf_path>")
    sys.exit(1)

pdf_path = sys.argv[1]

# R3 right-side columns are stable.
COLUMNS = {
    "r3_course": (865, 995),
    "r3_allotted_category": (995, 1035),
    "r3_candidate_category": (1035, 1088),
    "r3_option": (1088, 1125),
    "r3_remarks": (1125, 1186),
}

# Known quota names from the PDF legend.
# Longer patterns must be checked first.
QUOTA_PATTERNS = [
    ("Self-Financed Merit Seat", re.compile(
        r"Self-\s+(?:.*?\s+)?Financed\s+Merit\s+Seat",
        re.IGNORECASE
    )),
    ("Muslim Minority Quota", re.compile(
        r"Muslim\s+Minority\s+Quota",
        re.IGNORECASE
    )),
    ("Jain Minority Quota", re.compile(
        r"Jain\s+Minority\s+Quota",
        re.IGNORECASE
    )),
    ("Banaras Hindu University Quota", re.compile(
        r"Banaras\s+Hindu\s+University\s+Quota",
        re.IGNORECASE
    )),
    ("Aligarh Muslim University", re.compile(
        r"Aligarh\s+Muslim\s+University",
        re.IGNORECASE
    )),
    ("Armed Forces Medical", re.compile(
        r"Armed\s+Forces\s+Medical",
        re.IGNORECASE
    )),
    ("Delhi University Quota", re.compile(
        r"Delhi\s+University\s+Quota",
        re.IGNORECASE
    )),
    ("DNB Quota", re.compile(
        r"DNB\s+Quota",
        re.IGNORECASE
    )),
    ("IP University Quota", re.compile(
        r"IP\s+University\s+Quota",
        re.IGNORECASE
    )),
    ("All India", re.compile(
        r"All\s+India",
        re.IGNORECASE
    )),
    ("Non-Resident Indian", re.compile(
        r"Non-Resident\s+Indian",
        re.IGNORECASE
    )),
]


def get_column(x):
    for name, (x_min, x_max) in COLUMNS.items():
        if x_min <= x < x_max:
            return name
    return None


def extract_page_records(page):
    words = page.extract_words(
        x_tolerance=2,
        y_tolerance=3
    )

    words = sorted(words, key=lambda w: (w["top"], w["x0"]))

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
        line = sorted(line, key=lambda w: w["x0"])
        text = " ".join(w["text"] for w in line)

        match = re.match(r"^(\d+)\s+", text)

        if match:
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


def extract_r3_words(record):
    """
    Extract all words belonging to the R3 section before the course.
    The R3 section begins around x=575 and the course begins around x=865.
    """

    left_words = []

    for line in record["lines"]:
        for word in line:
            x = word["x0"]

            if 575 <= x < 865:
                left_words.append(word)

    return left_words


def reconstruct_quota_and_institute(record):
    """
    Reconstruct R3 quota and institute.

    The PDF wraps these two cells unpredictably, so fixed x boundaries
    are not sufficient. We identify the quota from known quota patterns
    and treat the remaining R3 text as institute.
    """

    words = extract_r3_words(record)

    if not words:
        return "", ""

    # Preserve PDF reading order.
    words = sorted(
        words,
        key=lambda w: (w["top"], w["x0"])
    )

    # Build text while keeping the positions of each word.
    text = " ".join(w["text"] for w in words)

    # Try to identify the quota.
    for quota_name, pattern in QUOTA_PATTERNS:

        match = pattern.search(text)

        if not match:
            continue

        quota_text = match.group(0)

        # Special handling for Self-Financed Merit Seat.
        #
        # The PDF sometimes interleaves institute words between
        # "Self-" and "Financed Merit Seat". Those words should
        # belong to the institute, not the quota.
        if quota_name == "Self-Financed Merit Seat":
            quota = quota_name

            # Find the actual words making up the quota.
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
                    if value.startswith("financed"):
                        financed_index = i
                        continue

                if financed_index is not None and merit_index is None:
                    if value.lower() == "merit":
                        merit_index = i
                        continue

                if merit_index is not None and seat_index is None:
                    if value.lower() == "seat":
                        seat_index = i
                        break

            if (
                self_index is not None
                and financed_index is not None
                and merit_index is not None
                and seat_index is not None
            ):
                quota_indices = {
                    self_index,
                    financed_index,
                    merit_index,
                    seat_index
                }

                institute_words = [
                    word["text"]
                    for i, word in enumerate(words)
                    if i not in quota_indices
                ]

                return quota, " ".join(institute_words).strip()

        # Normal quota handling.
        #
        # Find the words participating in the matched quota.
        match_start = match.start()
        match_end = match.end()

        positions = []
        current_position = 0

        for i, word in enumerate(words):
            word_start = current_position
            word_end = word_start + len(word["text"])

            if word_end >= match_start and word_start <= match_end:
                positions.append(i)

            current_position = word_end + 1

        quota_indices = set(positions)

        institute_words = [
            word["text"]
            for i, word in enumerate(words)
            if i not in quota_indices
        ]

        return quota_name, " ".join(institute_words).strip()

    # No recognized quota.
    # Keep the data rather than silently throwing it away.
    return "", text.strip()


def extract_r3_fields(record):
    fields = {
        "rank": record["rank"],
        "r3_quota": "",
        "r3_institute": "",
        "r3_course": [],
        "r3_allotted_category": [],
        "r3_candidate_category": [],
        "r3_option": [],
        "r3_remarks": [],
    }

    # Reconstruct quota + institute separately.
    quota, institute = reconstruct_quota_and_institute(record)

    fields["r3_quota"] = quota
    fields["r3_institute"] = institute

    # Extract stable right-side columns.
    for line in record["lines"]:
        for word in line:
            column = get_column(word["x0"])

            if column is not None:
                fields[column].append(word["text"])

    for key in fields:
        if key in ("rank", "r3_quota", "r3_institute"):
            continue

        fields[key] = " ".join(fields[key]).strip()

    return fields


# ------------------------------------------------------------
# Parse PDF
# ------------------------------------------------------------

all_records = []

print("Opening PDF...")
print()

with pdfplumber.open(pdf_path) as pdf:

    total_pages = len(pdf.pages)

    print(f"Total pages: {total_pages}")
    print("Parsing...")

    for page_number, page in enumerate(pdf.pages, start=1):

        records = extract_page_records(page)

        for record in records:
            fields = extract_r3_fields(record)
            fields["page_number"] = page_number
            all_records.append(fields)

        if page_number % 100 == 0:
            print(
                f"Processed {page_number}/{total_pages} pages "
                f"({len(all_records)} records)"
            )


# ------------------------------------------------------------
# Write CSV
# ------------------------------------------------------------

output_file = "round3_allotments.csv"

fieldnames = [
    "rank",
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
    encoding="utf-8"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(all_records)


print()
print("Done.")
print(f"Total records: {len(all_records)}")
print(f"Output: {output_file}")