import pdfplumber
import sys

# Import the parser functions from parse_round3.py
from parse_round3 import extract_page_records, extract_r3_fields

if len(sys.argv) != 2:
    print("Usage: python scripts/test_round3_parser.py <pdf_path>")
    sys.exit(1)

pdf_path = sys.argv[1]

TARGET_RANKS = {6, 10, 26, 30057, 30066, 230087}

found = {}

print("Opening PDF...")

with pdfplumber.open(pdf_path) as pdf:

    for page_number, page in enumerate(pdf.pages, start=1):

        records = extract_page_records(page)

        for record in records:

            rank = record["rank"]

            if rank in TARGET_RANKS:
                fields = extract_r3_fields(record)
                fields["page_number"] = page_number
                found[rank] = fields

        if len(found) == len(TARGET_RANKS):
            break


print()
print("=" * 100)
print("PARSER TEST RESULTS")
print("=" * 100)

for rank in sorted(TARGET_RANKS):

    print()
    print(f"RANK {rank}")
    print("-" * 100)

    if rank not in found:
        print("NOT FOUND")
        continue

    row = found[rank]

    print(f"Quota:              {row['r3_quota']}")
    print(f"Institute:           {row['r3_institute']}")
    print(f"Course:              {row['r3_course']}")
    print(f"Allotted Category:   {row['r3_allotted_category']}")
    print(f"Candidate Category:  {row['r3_candidate_category']}")
    print(f"Option:              {row['r3_option']}")
    print(f"Remarks:             {row['r3_remarks']}")
    print(f"PDF Page:            {row['page_number']}")

print()
print("=" * 100)
print("DONE")
print("=" * 100)