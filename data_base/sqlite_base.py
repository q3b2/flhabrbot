import logging

logging.basicConfig(filename="./info.log", filemode="a", level=logging.INFO,
                    format="%(asctime)s - [%(levelname)s] - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")


class cdb():
    def __init__(self):
        import sqlite3
        self.db_connection = sqlite3.connect("./rss.sqlite")
        self.db = self.db_connection.cursor()
        self.db.execute(
            'CREATE TABLE IF NOT EXISTS rss(user_id MEDIUMINT, user_name TEXT, user_rss TEXT, sended_order MEDIUMINT, datet TEXT)')
        logging.info("sql connected")

    def add_info(self, user_id, user_name, user_rss, send_order, date):
        self.db.execute("SELECT 1 FROM rss WHERE user_id=?", (user_id,))
        if self.db.fetchone():
            self.db.execute("UPDATE rss set user_name=?, user_rss=?, sended_order=?, datet=? WHERE user_id=?",
                            (user_name, user_rss, send_order, date, user_id))
            logging.info("edit item with user_id={}".format(str(user_id)))
        else:
            self.db.execute("INSERT INTO rss(user_id,user_name,user_rss,sended_order,datet) VALUES (?, ?, ?, ?, ?)",
                            (user_id, user_name, user_rss, send_order, date))
            logging.info("add item with user_id={}".format(str(user_id)))
        self.db_connection.commit()

    def add_send_order(self, user_id, i):
        self.db.execute(f"UPDATE rss set sended_order=sended_order+{i} WHERE user_id={user_id}")
        logging.info(f"sended order {i} {user_id}")
        self.db_connection.commit()

    def get_info(self, user_id):
        self.db.execute(f"SELECT * FROM rss WHERE user_id={user_id}")
        logging.info(f"item found user_id={user_id}")
        return self.db.fetchone()
