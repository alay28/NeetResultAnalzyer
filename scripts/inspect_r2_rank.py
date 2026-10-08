import pdfplumber

PDF_FILE = r"C:\Users\USER\Downloads\Round3-Neet.pdf"

rank_to_find = input("Enter rank: ").strip()

print()
print("Opening PDF...")

with pdfplumber.open(PDF_FILE) as pdf:
    for page_number, page in enumerate(pdf.pages, start=1):

        words = page.extract_words(
            x_tolerance=1,
            y_tolerance=3,
            keep_blank_chars=False
        )

        for word in words:
            if word["text"].strip() == rank_to_find:

                print()
                print("=" * 120)
                print(f"FOUND rank {rank_to_find} on page {page_number}")
                print("=" * 120)
                print()

                # Print every extracted word on the page with coordinates.
                for w in words:
                    print(
                        f"x0={w['x0']:8.2f} "
                        f"x1={w['x1']:8.2f} "
                        f"top={w['top']:8.2f} "
                        f"bottom={w['bottom']:8.2f} "
                        f"text={w['text']!r}"
                    )

                print()
                print("=" * 120)
                print("DONE")
                print("=" * 120)

                raise SystemExit