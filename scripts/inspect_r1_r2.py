import pdfplumber

PDF_FILE = r"C:\Users\USER\Downloads\Round3-Neet.pdf"

with pdfplumber.open(PDF_FILE) as pdf:

    page = pdf.pages[3]

    words = page.extract_words(
        x_tolerance=2,
        y_tolerance=3
    )

    words = sorted(
        words,
        key=lambda w: (w["top"], w["x0"])
    )

    printing = False

    for word in words:

        if word["text"] == "6" and word["x0"] < 40:
            printing = True

        if printing:
            print(
                f"{word['x0']:7.1f} | "
                f"{word['x1']:7.1f} | "
                f"{word['top']:7.1f} | "
                f"{word['text']}"
            )

        # Rank 10 starts after rank 6's row
        if printing and word["text"] == "10" and word["x0"] < 40:
            break