from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import jsonify
from flask import url_for
from flask import session
import twoFa
import requests
from flask_wtf import CSRFProtect
from flask_csp.csp import csp_header
import logging
from functools import wraps

import userManagement as dbHandler
import logmanager as devlogger

# Code snippet for logging a message
# app.logger.critical("message")

app_log = logging.getLogger(__name__)
logging.basicConfig(
    filename="security_log.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
)

# Generate a unique basic 16 key: https://acte.ltd/utils/randomkeygen
app = Flask(__name__)
app.secret_key = b"_53oi3uriq9pifpff;apl"
csrf = CSRFProtect(app)


# ensures user is authenticated
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in") or not session.get("email"):
            return redirect("/login.html")
        return f(*args, **kwargs)

    return decorated_function


# Redirect index.html to domain root for consistent UX
@app.route("/index", methods=["GET"])
@app.route("/index.htm", methods=["GET"])
@app.route("/index.asp", methods=["GET"])
@app.route("/index.php", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def root():
    return redirect("/", 302)


@app.route("/", methods=["POST", "GET"])
@csp_header(
    {
        # Server Side CSP is consistent with meta CSP in layout.html
        "base-uri": "'self'",
        "default-src": "'self'",
        "style-src": "'self'",
        "script-src": "'self'",
        "img-src": "'self' data:",
        "media-src": "'self'",
        "font-src": "'self'",
        "object-src": "'self'",
        "child-src": "'self'",
        "connect-src": "'self'",
        "worker-src": "'self'",
        "report-uri": "/csp_report",
        "frame-ancestors": "'none'",
        "form-action": "'self'",
        "frame-src": "'none'",
    }
)
def index():
    return render_template("/index.html")


@app.route("/profile.html", methods=["GET"])
@login_required
def profile():
    return render_template("/profile.html")


@app.route("/login.html", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        if dbHandler.authenticateUser(email, password):

            otp = twoFa.generate_otp()
            if twoFa.store_otp(email, otp) and twoFa.send_otp(email, otp):
                session["pending_email"] = email
                return redirect("/2fa.html")
            else:
                return render_template(
                    "/login.html", error="Failed to send verification code"
                )
        else:
            print("fail")
            return render_template("/login.html")
    else:
        return render_template("/login.html")


@app.route("/2fa.html", methods=["POST", "GET"])
def verify_2fa():
    if request.method == "POST":
        otp = request.form.get("otp", "").strip()
        email = session.get("pending_email")

        if not email:
            return redirect("/login.html")

        if twoFa.verify_otp(email, otp):
            session.pop("pending_email", None)
            session["logged_in"] = True
            session["email"] = email
            return redirect("/index.html")
        else:
            return render_template("2fa.html", error="incorrect otp")
    else:
        if not session.get("pending_email"):
            return redirect("/login.html")
        return render_template("/2fa.html")


@app.route("/logout.html", methods=["GET"])
def logout():
    session.clear()
    return redirect("/login.html")


@app.route("/signup.html", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        signedup = dbHandler.addUser(email, password)
        if signedup:
            return redirect("/login.html")
        else:
            return render_template("/signup.html", error="unable to add user")
    return render_template("/signup.html")


@app.route("/devlog.html", methods=["POST", "GET"])
@login_required
def devlog():

    if request.method == "POST":
        email = session.get("email")
        devname = request.form.get("devname", "")
        project = request.form.get("projectname", "")
        log = request.form.get("log", "")
        startdate = request.form.get("startdate", "")
        enddate = request.form.get("enddate", "")
        worktime = request.form.get("timeworked", "")
        repo = request.form.get("repo", "")

        logdone = devlogger.addlog(
            email, devname, project, log, startdate, enddate, worktime, repo
        )
        if logdone:
            return redirect("/profile.html")
        else:
            return render_template("/index.html", error="unable to add user")
    return render_template("/devlog.html")


@app.route("/devview.html", methods=["GET", "POST"])
@login_required
def devview():

    email = session.get("email")

    if request.method == "POST":
        # Get sort parameters from form
        sort_by = request.form.get("sort1", "date")
        order = request.form.get("order1", "DESC")
        sort_by2 = request.form.get("sort2", "")
        order2 = request.form.get("order2", "DESC")
        sort_by3 = request.form.get("sort3", "")
        order3 = request.form.get("order3", "DESC")
        search = request.form.get("search", "")
        searchdev = request.form.get("searchdev", "")

        # Build query string for redirect
        params = f"?sort1={sort_by}&order1={order}"
        if sort_by2:
            params += f"&sort2={sort_by2}&order2={order2}"
        if sort_by3:
            params += f"&sort3={sort_by3}&order3={order3}"
        if search:
            params += f"&search={search}"
        if searchdev:
            params += f"&searchdev={searchdev}"  # Added

        return redirect(f"/devview.html{params}")

    # GET request
    sort_by = request.args.get("sort1", "date")
    order = request.args.get("order1", "DESC")
    sort_by2 = request.args.get("sort2", "")
    order2 = request.args.get("order2", "DESC")
    sort_by3 = request.args.get("sort3", "")
    order3 = request.args.get("order3", "DESC")
    search = request.args.get("search", "")
    searchdev = request.args.get("searchdev", "")

    logs = devlogger.viewlog(
        sort_by,
        order,
        sort_by2,
        order2,
        sort_by3,
        order3,
        search,
        searchdev,
    )

    return render_template(
        "/devview.html",
        logs=logs,
        email=email,
        sort1=sort_by,
        order1=order,
        sort2=sort_by2,
        order2=order2,
        sort3=sort_by3,
        order3=order3,
        search=search,
        searchdev=searchdev,
    )


# Endpoint for logging CSP violations
# @app.route("/csp_report", methods=["POST"])


# @csrf.exempt
# def csp_report():
#     app.logger.critical(request.data.decode())
#     return "done"


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
