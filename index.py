from manager import Manager
from sqlqueries import QueriesSQLite


QueriesSQLite.create_tables()


if __name__ == "__main__":
    app = Manager()
    app.mainloop()