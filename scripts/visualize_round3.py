import csv
import re

import plotly.graph_objects as go


CSV_FILE = "round3_allotments.csv"
OUTPUT_FILE = "round3_analysis.html"


def normalize(text):
    return " ".join(text.strip().upper().split())


def extract_state(institute):
    states = [
        "ANDHRA PRADESH",
        "ARUNACHAL PRADESH",
        "ASSAM",
        "BIHAR",
        "CHHATTISGARH",
        "GOA",
        "GUJARAT",
        "HARYANA",
        "HIMACHAL PRADESH",
        "JHARKHAND",
        "KARNATAKA",
        "KERALA",
        "MADHYA PRADESH",
        "MAHARASHTRA",
        "MANIPUR",
        "MEGHALAYA",
        "MIZORAM",
        "NAGALAND",
        "ODISHA",
        "PUNJAB",
        "RAJASTHAN",
        "SIKKIM",
        "TAMIL NADU",
        "TELANGANA",
        "TRIPURA",
        "UTTAR PRADESH",
        "UTTARAKHAND",
        "WEST BENGAL",
        "DELHI",
        "CHANDIGARH",
        "JAMMU AND KASHMIR",
        "PUDUCHERRY",
    ]

    institute_upper = institute.upper()

    for state in states:
        if re.search(rf"\b{re.escape(state)}\b", institute_upper):
            return state.title()

    return "Unknown"


def main():
    print("=" * 100)
    print("ROUND 3 TABLE")
    print("=" * 100)
    print()

    min_rank = int(input("Minimum rank: ").strip())
    max_rank = int(input("Maximum rank: ").strip())
    course = input("Course: ").strip()
    candidate_category = input("Candidate category: ").strip()
    allotted_category = input("Allotted category: ").strip()

    print()
    print("Reading CSV...")

    matches = []

    with open(CSV_FILE, "r", encoding="utf-8-sig") as f:
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

            row["rank"] = rank
            row["state"] = extract_state(row["r3_institute"])

            matches.append(row)

    if not matches:
        print()
        print("No matching records found.")
        return

    # Sort everything by rank first
    matches.sort(key=lambda row: row["rank"])

    # ---------------------------------------------------------
    # Group records by state
    # ---------------------------------------------------------

    states = {}

    for row in matches:
        state = row["state"]

        if state not in states:
            states[state] = []

        states[state].append(row)

    # Sort states alphabetically
    sorted_states = sorted(states.keys())

    print()
    print(f"Matches found: {len(matches)}")
    print(f"States found: {len(sorted_states)}")

    for state in sorted_states:
        print(
            f"  {state}: {len(states[state])} allotments"
        )

    print()
    print("Creating HTML tables...")

    # ---------------------------------------------------------
    # Create one table per state
    # ---------------------------------------------------------

    figures = []

    for state in sorted_states:
        state_matches = states[state]

        headers = [
            "Allotted Rank",
            "College / Institute",
            "Course",
            "Quota",
            "Allotted Category",
            "Candidate Category",
            "Option No.",
            "Remarks",
        ]

        values = [
            [f"{row['rank']:,}" for row in state_matches],
            [row["r3_institute"] for row in state_matches],
            [row["r3_course"] for row in state_matches],
            [row["r3_quota"] for row in state_matches],
            [row["r3_allotted_category"] for row in state_matches],
            [row["r3_candidate_category"] for row in state_matches],
            [row["r3_option"] for row in state_matches],
            [row["r3_remarks"] for row in state_matches],
        ]

        figure = go.Figure(
            data=[
                go.Table(
                    columnwidth=[
                        90,
                        350,
                        180,
                        150,
                        130,
                        130,
                        80,
                        180,
                    ],
                    header=dict(
                        values=headers,
                        align="left",
                        font=dict(size=13),
                        height=35,
                    ),
                    cells=dict(
                        values=values,
                        align="left",
                        font=dict(size=12),
                        height=30,
                    ),
                )
            ]
        )

        figure.update_layout(
            title=f"{state} ({len(state_matches)} allotments)",
            height=max(
                250,
                100 + len(state_matches) * 35
            ),
            margin=dict(
                l=20,
                r=20,
                t=70,
                b=20,
            ),
        )

        figures.append(
            figure.to_html(
                full_html=False,
                include_plotlyjs=False,
            )
        )

    # ---------------------------------------------------------
    # Build complete HTML page
    # ---------------------------------------------------------

    title = (
        "NEET-PG Round 3 Allotments | "
        f"Ranks {min_rank:,}–{max_rank:,} | "
        f"{course}"
    )

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">

    <title>{title}</title>

    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>

    <style>

        body {{
            font-family: Arial, sans-serif;
            margin: 30px;
            background: #f5f5f5;
        }}

        .container {{
            max-width: 1800px;
            margin: auto;
        }}

        .summary {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 25px;
        }}

        .summary h1 {{
            margin-top: 0;
        }}

        .state-section {{
            background: white;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 10px;
        }}

        .state-title {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }}

        .count {{
            color: #666;
            font-size: 16px;
            font-weight: normal;
        }}

    </style>
</head>

<body>

<div class="container">

    <div class="summary">

        <h1>NEET-PG Round 3 Allotments</h1>

        <p>
            <b>Rank range:</b>
            {min_rank:,} – {max_rank:,}
        </p>

        <p>
            <b>Course:</b>
            {course}
        </p>

        <p>
            <b>Candidate Category:</b>
            {candidate_category}
        </p>

        <p>
            <b>Allotted Category:</b>
            {allotted_category}
        </p>

        <p>
            <b>Total matching allotments:</b>
            {len(matches)}
        </p>

        <p>
            <b>States:</b>
            {len(sorted_states)}
        </p>

    </div>
"""

    for state, figure_html in zip(sorted_states, figures):

        html += f"""
    <div class="state-section">

        <div class="state-title">
            {state}
            <span class="count">
                ({len(states[state])} allotments)
            </span>
        </div>

        {figure_html}

    </div>
"""

    html += """
</div>

</body>
</html>
"""

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(html)

    print()
    print("=" * 100)
    print(f"HTML saved to: {OUTPUT_FILE}")
    print("Opening visualization in your browser...")
    print("=" * 100)

    import webbrowser

    webbrowser.open(OUTPUT_FILE)


if __name__ == "__main__":
    main()