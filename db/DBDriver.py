import peewee, sqlite3


def create_db(self, db_name):
    self.conn = sqlite3.connect(db_name)
    sql = 'CREATE TABLE files  ' \
            '(name text)'
    self.conn.execute(sql)

