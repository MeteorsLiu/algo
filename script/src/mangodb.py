import logging
import os
from dotenv import load_dotenv
from pymongo import MongoClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

log = logger = logging

load_dotenv()

GITHUB_ACCESS_TOKEN = os.environ.get('GITHUB_ACCESS_TOKEN')
MONGODB_IP = os.environ.get('MONGODB_IP')
MONGODB_PORT = os.environ.get('MONGODB_PORT')
MONGODB_USENAME = os.environ.get('MONGODB_USENAME')
MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD')

class Mangodb():
    def __init__(self, timeout: int = 40000) -> None:
        self.client = MongoClient(f"mongodb://{MONGODB_USENAME}:{MONGODB_PASSWORD}@{MONGODB_IP}:{MONGODB_PORT}/")
        log.info(self.client)
        self.algodb = self.client['algodb']
        # user_info collection structure
        # username update_time issues pullrequests discussions
        self.user_info = self.algodb["user_info"]
        self.user_issue = self.algodb['user_issue']
        self.user_pr = self.algodb['user_pr']
        self.user_discussion = self.algodb['user_discussion']
        self.repo_info = self.algodb['repo_info']