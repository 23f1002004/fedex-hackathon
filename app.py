from flask import Flask, render_template, request, redirect, session
import csv
from data import users, dcas, cases
import random

app = Flask(__name__)
app.secret_key = "hackathon_secret"

dcas = {
    "alpha": {"cost": 12, "score": 80},
    "beta": {"cost": 10, "score": 70},
    "gamma": {"cost": 8, "score": 60},
}

# ---------- UTILS ----------
def case_priority(days, amount):
    return round((0.6 * days) + (0.4 * amount / 1000), 2)

def update_dca_scores():
    """
    Simulate real-world performance changes
    """
    for dca in dcas:
        fluctuation = random.randint(-5, 5)
        dcas[dca]["score"] = max(50, dcas[dca]["score"] + fluctuation)


def assign_dca(case_priority):
    """
    Assign DCA based on:
    - Case priority
    - DCA score
    """
    update_dca_scores()
    # Sort DCAs by score (high to low)
    sorted_dcas = sorted(
        dcas.items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )

    # High priority → top DCA
    if case_priority >= 80:
        return sorted_dcas[0][0]

    # Medium priority → middle DCA
    elif case_priority >= 50:
        return sorted_dcas[len(sorted_dcas)//2][0]

    # Low priority → lowest DCA
    else:
        return sorted_dcas[-1][0]


# ---------- LOGIN ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username", "").strip()
        p = request.form.get("password", "").strip()

        print("DEBUG USER:", repr(u))
        print("DEBUG PASS:", repr(p))
        print("AVAILABLE USERS:", users.keys())

        if u in users and users[u]["password"] == p:
            session.clear()
            session["user"] = u
            session["role"] = users[u]["role"]

            print("LOGIN SUCCESS:", session)

            if session["role"] == "fedex":
                return redirect("/fedex")
            else:
                return redirect("/dca")
        else:
            print("LOGIN FAILED")

    return render_template("login.html")



@app.route("/fedex/verify")
def verify_cases():
    if session.get("role") != "fedex":
        return redirect("/")

    claimed_cases = [
        (i, c) for i, c in enumerate(cases)
        if c["status"] == "Claimed Solved"
    ]

    return render_template(
        "fedex_verify.html",
        cases=claimed_cases
    )



# ---------- FEDEX ----------
@app.route("/fedex", methods=["GET", "POST"])
def fedex():
    if session.get("role") != "fedex":
        return redirect("/")

    if request.method == "POST":
        customer = request.form["customer"]
        amount = int(request.form["amount"])
        days = int(request.form["days"])

        priority = case_priority(days, amount)
        dca = assign_dca(priority)

        cases.append({
    "customer": customer,
    "amount": amount,
    "days": days,
    "priority": priority,
    "dca": dca,
    "status": "Open",              # Open / Claimed Solved / Verified Solved / Rejected
    "sla_penalty": False,
    "recovered_amount": 0
})


    return render_template("fedex_dashboard.html", cases=cases, dcas=dcas)

@app.route("/fedex/analytics")
def fedex_analytics():
    if session.get("role") != "fedex":
        return redirect("/")

    stats = {}

    for dca in dcas:
        stats[dca] = {
            "assigned": 0,
            "solved": 0,
            "penalties": 0,
            "recovered": 0
        }

    for c in cases:
        d = c["dca"]
        stats[d]["assigned"] += 1

        if c["status"] == "Verified Solved":
            stats[d]["solved"] += 1
            stats[d]["recovered"] += c["recovered_amount"]

        if c["sla_penalty"]:
            stats[d]["penalties"] += 1

    return render_template(
        "fedex_analytics.html",
        stats=stats
    )
    
@app.route("/fedex/approve/<int:i>")
def approve_case(i):
    if session.get("role") == "fedex":
        cases[i]["status"] = "Verified Solved"
        cases[i]["recovered_amount"] = cases[i]["amount"]
    return redirect("/fedex/verify")


@app.route("/fedex/reject/<int:i>")
def reject_case(i):
    if session.get("role") == "fedex":
        cases[i]["status"] = "Rejected"
        cases[i]["sla_penalty"] = True
    return redirect("/fedex/verify")

@app.route("/upload", methods=["POST"])
def upload_csv():
    if session.get("role") != "fedex":
        return redirect("/")

    file = request.files["file"]
    reader = csv.reader(file.stream.read().decode("utf-8").splitlines())

    for row in reader:
        customer, amount, days = row
        priority = case_priority(int(days), int(amount))
        dca = assign_dca()

        cases.append({
            "customer": customer,
            "amount": int(amount),
            "days": int(days),
            "priority": priority,
            "dca": dca,
            "status": "Open",
            "sla_penalty": False
        })

    return redirect("/fedex")


# ---------- DCA ----------
@app.route("/dca")
def dca():
    if session.get("role") != "dca":
        return redirect("/")

    dca_user = session["user"]

    dca_cases = sorted(
        [c for c in cases if c["dca"] == dca_user],
        key=lambda x: x["priority"],
        reverse=True
    )

    resolved = sum(1 for c in dca_cases if c["status"] == "Verified Solved")
    penalties = sum(1 for c in dca_cases if c["sla_penalty"])

    score = max(0, 100 + resolved * 5 - penalties * 10)
    dcas[dca_user]["score"] = score

    return render_template(
        "dca_dashboard.html",
        cases=dca_cases,
        resolved=resolved,
        penalties=penalties,
        score=score
    )


@app.route("/claim/<int:i>")
def claim_solved(i):
    if session.get("role") == "dca":
        cases[i]["status"] = "Claimed Solved"
    return redirect("/dca")


@app.route("/penalty/<int:i>")
def penalty(i):
    if session.get("role") == "dca":
        cases[i]["sla_penalty"] = True
    return redirect("/dca")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
