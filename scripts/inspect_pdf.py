import pdfplumber
import sys

if len(sys.argv) != 2:
    print("Usage: python scripts/inspect_pdf.py <pdf_path>")
    sys.exit(1)

pdf_path = sys.argv[1]

with pdfplumber.open(pdf_path) as pdf:

    page = pdf.pages[4]

    words = page.extract_words(
        x_tolerance=2,
        y_tolerance=3
    )

    # Sort words from top to bottom
    words = sorted(words, key=lambda w: (w["top"], w["x0"]))

    # First group words into visual lines
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

    print("\n--- VISUAL LINES ---\n")

    for line in lines:

        line = sorted(line, key=lambda w: w["x0"])

        text = " ".join(w["text"] for w in line)

        print(
            f"Y={line[0]['top']:6.1f} | {text}"
        )