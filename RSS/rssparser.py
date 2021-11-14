from data_base.sqlite_base import cdb
import logging, time

logging.basicConfig(filename="./info.log", filemode="a", level=logging.INFO,
                    format="%(asctime)s - [%(levelname)s] - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")


class parsRSS():
    def __init__(self):
        self.db = cdb()

    def get_new_feed(self, user_id):
        import feedparser

        url = self.db.get_info(user_id=user_id)[2]
        pars = feedparser.parse(url)["entries"]
        new_feed = list()
        logging.info("parsed successful")
        info = self.db.get_info(user_id=user_id)
        for i in range(pars.__len__()):

            if time.mktime(pars[i]["published_parsed"]) >= float(info[4])-21599:
                new_feed.append(pars[i])
            else:
                break
        self.db.add_info(user_id, *info[1:-1], date=time.mktime(pars[0]["published_parsed"])+21600)
        logging.info(f"for user_id={user_id} found {len(new_feed)}")
        return new_feed
