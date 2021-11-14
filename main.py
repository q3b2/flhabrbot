import logging
from tBot.tBot import tb
logging.basicConfig(filename="./info.log", filemode="a", level=logging.INFO,
                    format="%(asctime)s - [%(levelname)s] - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")
logging.info("Program started")

if __name__ == "__main__":
    tb(token="")
