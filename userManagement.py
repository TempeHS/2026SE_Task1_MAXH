import sqlite3 as sql
import bcrypt


### example
def getUsers():
    con = sql.connect("databaseFiles/logins.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM logins")
    con.close()
    return cur


def authenticateUser(email, password):
    try:
        # connects to database
        con = sql.connect("databaseFiles/database.db")
        cur = con.cursor()
        cur.execute("select password from logins where email = ?", (email,))
        row = cur.fetchone()
        con.close()

        hashedpw = row[0]
        return bcrypt.checkpw(password.encode("utf-8"), hashedpw.encode("utf-8"))

    except Exception as i:
        print(f"auth error {i}")
        return False


# session managment


# function for adding a user
def addUser(email, password):
    try:
        # connects to database
        con = sql.connect("databaseFiles/database.db")
        cur = con.cursor()
        # hashes the password gotten from the signup page - main.py
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
            "utf-8"
        )
        # adds the logins hopefully securely need to check
        cur.execute(
            "insert into logins (email, password) Values (?, ?)", (email, hashed)
        )
        # disconnects from database and commits
        con.commit()
        con.close()
        return True
    # error catch for existing user
    except sql.IntegrityError:
        return False
    # throws an error to the terminal
    except Exception as e:
        print(f"erro {e} r")
        return False
