import sqlite3 as sql
import bcrypt


def addlog(email, devname, project, log, startdate, enddate, worktime, repo):
    try:
        con = sql.connect("databaseFiles/database.db")
        cur = con.cursor()
        cur.execute(
            "insert into devlog (email, developer, project, devlog, startdate, endate, timeworked, repo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (email, devname, project, log, startdate, enddate, worktime, repo),
        )
        con.commit()
        con.close()
        return True
    except sql.IntegrityError as e:
        print(f"Integrity error: {e}")
        return False
    except Exception as e:
        print(f"erro {e} r")
        return False


def viewlog(
    email,
    sort_by=None,
    order=None,
    sort_by2=None,
    order2=None,
    sort_by3=None,
    order3=None,
    search=None,
):
    try:
        con = sql.connect("databaseFiles/database.db")
        cur = con.cursor()

        # allowed sorts
        allowed_sorts = {
            "date": "date",
            "startdate": "startdate",
            "enddate": "endate",
            "developer": "developer",
            "project": "project",
            "repo": "repo",
            "timeworked": "timeworked",
        }

        constraint_clause = "where email = ?"
        params = [email]

        if search:
            constraint_clause += " and devlog like ?"
            params.append(f"%{search}%")

        # Build ORDER BY clause
        order_clauses = []

        # Primary sort
        if sort_by and sort_by in allowed_sorts:
            order1 = (
                order.upper() if order and order.upper() in ["ASC", "DESC"] else "DESC"
            )
            order_clauses.append(f"{allowed_sorts[sort_by]} {order1}")

        # Secondary sort
        if sort_by2 and sort_by2 in allowed_sorts:
            order2_val = (
                order2.upper()
                if order2 and order2.upper() in ["ASC", "DESC"]
                else "DESC"
            )
            order_clauses.append(f"{allowed_sorts[sort_by2]} {order2_val}")

        # Tertiary sort
        if sort_by3 and sort_by3 in allowed_sorts:
            order3_val = (
                order3.upper()
                if order3 and order3.upper() in ["ASC", "DESC"]
                else "DESC"
            )
            order_clauses.append(f"{allowed_sorts[sort_by3]} {order3_val}")

        # Default to date DESC if no sorts specified
        if not order_clauses:
            order_clauses.append("date DESC")

        query = f"SELECT developer, project, devlog, startdate, endate, timeworked, date, repo FROM devlog {constraint_clause} ORDER BY {', '.join(order_clauses)}"

        cur.execute(query, params)
        logs = cur.fetchall()
        con.close()
        return logs
    except Exception as e:
        print(f"Error retrieving logs: {e}")
        return False


def editlog():
    pass
