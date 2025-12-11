import sqlite3 as sql
import bcrypt


### example
def getUsers():
    con = sql.connect("databaseFiles/logins.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM logins")
    con.close()
    return cur


def authenticateUser(email, password): ...


def addUser(email, password):
    try:
        con = sql.connect("databaseFiles/database.db")
        cur = con.cursor()
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
            "utf-8"
        )
        cur.execute(
            "insert into logins (email, password) Values (?, ?)", (email, hashed)
        )
        con.commit()
        con.close()
        return True

    except sql.IntegrityError:
        return False
    except Exception as e:
        print(f"erro {e} r")
        return False
