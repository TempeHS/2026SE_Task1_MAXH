import sqlite3 as sql
import bcrypt


### example
def getUsers():
    con = sql.connect("databaseFiles/logins.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM id7-tusers")
    con.close()
    return cur

def authenticateUser(email, password):
    

def addUser (email, password)
    try:
        con = sql.connect("databaseFiles/logins.db")
        cur = con.cursor()

        cur.execute(
            "insert into logins (email, password) Values"
            (email, password)
        )

        con.commit()
        con.close()
        return True

    except sql.IntegrityError:
        return False
    except Exception as e:
        print(f"erro {e} r")
        return False
