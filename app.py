from flask import Flask, render_template_string, request
import csv
import re

app = Flask(__name__)

CSV_FILE = "round3_allotments.csv"


def load_data():
    with open(CSV_FILE, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


data = load_data()


def get_unique_values(column):
    values = {
        row[column].strip()
        for row in data
        if row[column].strip()
    }

    return sorted(values, key=str.upper)


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
        if re.search(
            rf"\b{re.escape(state)}\b",
            institute_upper
        ):
            return state.title()

    return "Unknown"


ROUNDS = {
    "1": {
        "label": "Round 1",
        "course": "r1_course",
        "quota": "r1_quota",
        "institute": "r1_institute",
        "remarks": "r1_remarks",
        "has_categories": False,
    },
    "2": {
        "label": "Round 2",
        "course": "r2_course",
        "quota": "r2_quota",
        "institute": "r2_institute",
        "remarks": "r2_remarks",
        "has_categories": False,
    },
    "3": {
        "label": "Round 3",
        "course": "r3_course",
        "quota": "r3_quota",
        "institute": "r3_institute",
        "remarks": "r3_remarks",
        "allotted_category": "r3_allotted_category",
        "candidate_category": "r3_candidate_category",
        "option": "r3_option",
        "has_categories": True,
    },
}


# Course lists for each round
round_courses = {
    round_number: get_unique_values(config["course"])
    for round_number, config in ROUNDS.items()
}


candidate_categories = get_unique_values(
    "r3_candidate_category"
)

allotted_categories = get_unique_values(
    "r3_allotted_category"
)


@app.route("/", methods=["GET", "POST"])
def home():

    matches = []
    search_performed = False

    selected_round = "3"

    min_rank = ""
    max_rank = ""
    selected_course = ""
    selected_candidate_category = ""
    selected_allotted_category = ""

    round_config = ROUNDS[selected_round]

    if request.method == "POST":

        search_performed = True

        selected_round = request.form.get(
            "round",
            "3"
        ).strip()

        if selected_round not in ROUNDS:
            selected_round = "3"

        round_config = ROUNDS[selected_round]

        min_rank = request.form.get(
            "min_rank",
            ""
        ).strip()

        max_rank = request.form.get(
            "max_rank",
            ""
        ).strip()

        selected_course = request.form.get(
            "course",
            ""
        ).strip()

        selected_candidate_category = request.form.get(
            "candidate_category",
            ""
        ).strip()

        selected_allotted_category = request.form.get(
            "allotted_category",
            ""
        ).strip()

        min_rank_value = int(min_rank)
        max_rank_value = int(max_rank)

        for row in data:

            rank = int(row["rank"])

            if rank < min_rank_value or rank > max_rank_value:
                continue

            # Course filter
            if (
                row[round_config["course"]].strip()
                != selected_course
            ):
                continue

            # Category filters only apply to Round 3
            if selected_round == "3":

                if (
                    row["r3_candidate_category"].strip()
                    != selected_candidate_category
                ):
                    continue

                if (
                    row["r3_allotted_category"].strip()
                    != selected_allotted_category
                ):
                    continue

            row_copy = row.copy()

            row_copy["rank"] = rank

            row_copy["state"] = extract_state(
                row[round_config["institute"]]
            )

            matches.append(row_copy)

        matches.sort(
            key=lambda row: row["rank"]
        )

    states = {}

    for row in matches:

        state = row["state"]

        if state not in states:
            states[state] = []

        states[state].append(row)

    return render_template_string(
        """
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>NEET-PG Allotment Analyzer</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            color: #1f2937;
        }

        .header {
            background: #1f2937;
            color: white;
            padding: 28px 20px;
        }

        .header-content {
            max-width: 1200px;
            margin: auto;
        }

        .header h1 {
            margin: 0;
            font-size: 28px;
        }

        .header p {
            margin: 8px 0 0;
            color: #d1d5db;
            font-size: 15px;
        }

        .container {
            max-width: 1400px;
            margin: 30px auto;
            padding: 0 20px;
        }

        .card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            margin-bottom: 25px;
        }

        .card-title {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 20px;
        }

        .filters {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }

        .field {
            display: flex;
            flex-direction: column;
            gap: 7px;
        }

        .field label {
            font-size: 14px;
            font-weight: 600;
            color: #374151;
        }

        input,
        select {
            width: 100%;
            padding: 11px 12px;
            border: 1px solid #d1d5db;
            border-radius: 7px;
            font-size: 15px;
            background: white;
        }

        input:focus,
        select:focus {
            outline: none;
            border-color: #4f46e5;
        }

        .rank-range {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }

        .button-container {
            margin-top: 25px;
            display: flex;
            justify-content: flex-end;
        }

        .search-button {
            border: none;
            background: #4f46e5;
            color: white;
            padding: 12px 24px;
            border-radius: 7px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
        }

        .search-button:hover {
            background: #4338ca;
        }

        .results-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .results-count {
            color: #6b7280;
            font-size: 14px;
        }

        .state-section {
            margin-top: 30px;
        }

        .state-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .state-name {
            font-size: 19px;
            font-weight: bold;
        }

        .seat-count {
            color: #6b7280;
            font-size: 14px;
        }

        .table-wrapper {
            overflow-x: auto;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            min-width: 850px;
        }

        th {
            background: #f9fafb;
            color: #374151;
            font-size: 13px;
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #e5e7eb;
            white-space: nowrap;
        }

        td {
            padding: 12px;
            border-bottom: 1px solid #e5e7eb;
            font-size: 14px;
            vertical-align: top;
        }

        tr:last-child td {
            border-bottom: none;
        }

        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: #6b7280;
        }

        .hidden {
            display: none;
        }

        @media (max-width: 700px) {

            .header h1 {
                font-size: 23px;
            }

            .container {
                margin-top: 20px;
                padding: 0 12px;
            }

            .card {
                padding: 18px;
            }

            .filters {
                grid-template-columns: 1fr;
            }

            .button-container {
                justify-content: stretch;
            }

            .search-button {
                width: 100%;
            }

        }

    </style>

</head>


<body>


<header class="header">

    <div class="header-content">

        <h1>
            NEET-PG Allotment Analyzer
        </h1>

        <p>
            Analyze counselling allotments by rank,
            course, category and state
        </p>

    </div>

</header>


<main class="container">


    <!-- FILTER CARD -->

    <div class="card">

        <div class="card-title">
            Find Allotments
        </div>


        <form method="POST">

            <div class="filters">


                <!-- ROUND -->

                <div class="field">

                    <label for="round">
                        Counselling Round
                    </label>

                    <select
                        id="round"
                        name="round"
                        onchange="updateRoundFields()"
                    >

                        {% for round_number, round in rounds.items() %}

                        <option
                            value="{{ round_number }}"
                            {% if round_number == selected_round %}
                                selected
                            {% endif %}
                        >
                            {{ round.label }}
                        </option>

                        {% endfor %}

                    </select>

                </div>


                <!-- COURSE -->

                <div class="field">

                    <label for="course">
                        Course
                    </label>

                    <select
                        id="course"
                        name="course"
                        required
                    >

                        <option value="">
                            Select course
                        </option>

                        {% for course in courses %}

                        <option
                            value="{{ course }}"
                            {% if course == selected_course %}
                                selected
                            {% endif %}
                        >
                            {{ course }}
                        </option>

                        {% endfor %}

                    </select>

                </div>


                <!-- RANK -->

                <div class="field">

                    <label>
                        Rank Range
                    </label>

                    <div class="rank-range">

                        <input
                            type="number"
                            name="min_rank"
                            placeholder="Minimum rank"
                            value="{{ min_rank }}"
                            required
                        >

                        <input
                            type="number"
                            name="max_rank"
                            placeholder="Maximum rank"
                            value="{{ max_rank }}"
                            required
                        >

                    </div>

                </div>


                <!-- CANDIDATE CATEGORY -->

                <div
                    class="field"
                    id="candidate-category-field"
                >

                    <label for="candidate-category">
                        Candidate Category
                    </label>

                    <select
                        id="candidate-category"
                        name="candidate_category"
                        {% if selected_round != "3" %}
                            disabled
                        {% endif %}
                    >

                        <option value="">
                            Select category
                        </option>

                        {% for category in candidate_categories %}

                        <option
                            value="{{ category }}"
                            {% if category == selected_candidate_category %}
                                selected
                            {% endif %}
                        >
                            {{ category }}
                        </option>

                        {% endfor %}

                    </select>

                </div>


                <!-- ALLOTTED CATEGORY -->

                <div
                    class="field"
                    id="allotted-category-field"
                >

                    <label for="allotted-category">
                        Allotted Category
                    </label>

                    <select
                        id="allotted-category"
                        name="allotted_category"
                        {% if selected_round != "3" %}
                            disabled
                        {% endif %}
                    >

                        <option value="">
                            Select category
                        </option>

                        {% for category in allotted_categories %}

                        <option
                            value="{{ category }}"
                            {% if category == selected_allotted_category %}
                                selected
                            {% endif %}
                        >
                            {{ category }}
                        </option>

                        {% endfor %}

                    </select>

                </div>


            </div>


            <div class="button-container">

                <button
                    type="submit"
                    class="search-button"
                >
                    🔎 Find Allotments
                </button>

            </div>

        </form>

    </div>


    <!-- RESULTS -->

    <div class="card">

        <div class="results-header">

            <div class="card-title">
                Results
            </div>

            <div class="results-count">

                {% if search_performed %}

                    {{ matches|length }} allotments found

                {% else %}

                    No search performed

                {% endif %}

            </div>

        </div>


        {% if not search_performed %}

            <div class="empty-state">

                <p>
                    Select your filters and click
                    <b>Find Allotments</b>
                    to see matching seats.
                </p>

            </div>


        {% elif not matches %}

            <div class="empty-state">

                <p>
                    No matching allotments found.
                </p>

            </div>


        {% else %}


            {% for state, state_matches in states.items() %}

            <div class="state-section">

                <div class="state-header">

                    <div class="state-name">
                        {{ state }}
                    </div>

                    <div class="seat-count">
                        {{ state_matches|length }} allotments
                    </div>

                </div>


                <div class="table-wrapper">

                    <table>

                        <thead>

                            <tr>

                                <th>
                                    Allotted Rank
                                </th>

                                <th>
                                    College / Institute
                                </th>

                                <th>
                                    Course
                                </th>

                                <th>
                                    Quota
                                </th>

                                {% if selected_round == "3" %}

                                <th>
                                    Allotted Category
                                </th>

                                <th>
                                    Candidate Category
                                </th>

                                <th>
                                    Option No.
                                </th>

                                {% endif %}

                                <th>
                                    Remarks
                                </th>

                            </tr>

                        </thead>


                        <tbody>

                            {% for row in state_matches %}

                            <tr>

                                <td>
                                    <b>
                                        {{ "{:,}".format(row.rank) }}
                                    </b>
                                </td>

                                <td>
                                    {{ row[round_config.institute] }}
                                </td>

                                <td>
                                    {{ row[round_config.course] }}
                                </td>

                                <td>
                                    {{ row[round_config.quota] }}
                                </td>


                                {% if selected_round == "3" %}

                                <td>
                                    {{ row.r3_allotted_category }}
                                </td>

                                <td>
                                    {{ row.r3_candidate_category }}
                                </td>

                                <td>
                                    {{ row.r3_option }}
                                </td>

                                {% endif %}


                                <td>
                                    {{ row[round_config.remarks] }}
                                </td>

                            </tr>

                            {% endfor %}

                        </tbody>

                    </table>

                </div>

            </div>

            {% endfor %}


        {% endif %}


    </div>


</main>


<script>

const roundCourses = {{ round_courses | tojson }};


function updateRoundFields() {

    const round =
        document.getElementById("round").value;

    const courseSelect =
        document.getElementById("course");

    const candidateField =
        document.getElementById(
            "candidate-category-field"
        );

    const candidateSelect =
        document.getElementById(
            "candidate-category"
        );

    const allottedField =
        document.getElementById(
            "allotted-category-field"
        );

    const allottedSelect =
        document.getElementById(
            "allotted-category"
        );


    /*
     * Update courses
     */

    courseSelect.innerHTML =
        '<option value="">Select course</option>';

    const courses =
        roundCourses[round] || [];

    courses.forEach(function(course) {

        const option =
            document.createElement("option");

        option.value = course;
        option.textContent = course;

        courseSelect.appendChild(option);

    });


    /*
     * Round 3 has category filters.
     * Round 1 and Round 2 do not.
     */

    if (round === "3") {

        candidateField.classList.remove("hidden");
        allottedField.classList.remove("hidden");

        candidateSelect.disabled = false;
        allottedSelect.disabled = false;

        candidateSelect.required = true;
        allottedSelect.required = true;

    } else {

        candidateField.classList.add("hidden");
        allottedField.classList.add("hidden");

        candidateSelect.disabled = true;
        allottedSelect.disabled = true;

        candidateSelect.required = false;
        allottedSelect.required = false;

        candidateSelect.value = "";
        allottedSelect.value = "";

    }

}


/*
 * When the page first loads, make sure
 * the course list matches the selected round.
 */

document.addEventListener(
    "DOMContentLoaded",
    function() {

        const round =
            document.getElementById("round").value;

        const selectedCourse =
            {{ selected_course | tojson }};

        const courseSelect =
            document.getElementById("course");

        courseSelect.innerHTML =
            '<option value="">Select course</option>';

        const courses =
            roundCourses[round] || [];

        courses.forEach(function(course) {

            const option =
                document.createElement("option");

            option.value = course;
            option.textContent = course;

            if (course === selectedCourse) {
                option.selected = true;
            }

            courseSelect.appendChild(option);

        });

    }
);

</script>


</body>

</html>
        """,

        rounds=ROUNDS,
        round_courses=round_courses,
        courses=round_courses[selected_round],
        candidate_categories=candidate_categories,
        allotted_categories=allotted_categories,
        matches=matches,
        states=states,
        search_performed=search_performed,
        min_rank=min_rank,
        max_rank=max_rank,
        selected_course=selected_course,
        selected_candidate_category=selected_candidate_category,
        selected_allotted_category=selected_allotted_category,
        selected_round=selected_round,
        round_config=round_config,
    )


if __name__ == "__main__":
    app.run(debug=True)