
import requests
import time
import logging
import numpy as np
import pandas as pd
import os
from dotenv import load_dotenv
import argparse
from pymongo import MongoClient
from tqdm import tqdm
from typing import Literal
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

log = logger = logging

load_dotenv()

GITHUB_USERNAME = os.environ.get('GITHUB_USERNAME')
GITHUB_COOKIE = os.environ.get('GITHUB_COOKIE')
GITHUB_ACCESS_TOKEN = os.environ.get('GITHUB_ACCESS_TOKEN')
MONGODB_IP = os.environ.get('MONGODB_IP')
MONGODB_PORT = os.environ.get('MONGODB_PORT')
MONGODB_USENAME = os.environ.get('MONGODB_USENAME')
MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD')

class PCAT():
    def __init__(self, timeout: int = 30000) -> None:
        self.client = MongoClient(f"mongodb://{MONGODB_USENAME}:{MONGODB_PASSWORD}@{MONGODB_IP}:{MONGODB_PORT}/", 
                                  connectTimeoutMS=timeout, socketTimeoutMS=timeout)
        log.info(self.client)
        self.algodb = self.client['algodb']
        self.user_info = self.algodb["user_info"]
        self.user_issue = self.algodb['user_issue']
        self.user_pr = self.algodb['user_pr']
        self.user_discussion = self.algodb['user_discussion']
        self.repo_info = self.algodb['repo_info']
        
    def perform_pca(self, n_components=2):
        pca = PCA(n_components=n_components)

        principal_components = pca.fit_transform(self.df)

        pca_df = pd.DataFrame(
            principal_components,
            # columns=[f'PC{i + 1}' for i in range(n_components)]
            columns=[f'PC@{i}' for i in self.df.columns]
        )
        log.info(pca_df.describe())
        log.info(pca_df.head(10))
        log.info(pca.explained_variance_ratio_)
        return pca_df, pca.explained_variance_ratio_

    def load_repo_statics(self, limit: int = 0):
        self.repo_cursor = self.repo_info.find(
            {
                '$and' : [
                    {'stargazers_count': {'$gt': 0}},
                    {'forks_count': {'$gt': 0}},
                    {'watchers_count': {'$gt': 0}},
                    {'subscribers_count': {'$gt': 0}},
                    {'open_issues_count': {'$gt': 0}}
                ]
            },
            {
                '_id': 0,
                'stargazers_count': 1,
                'forks_count': 1,
                'watchers_count': 1,
                'subscribers_count': 1,
                'open_issues_count': 1
            }
        ).limit(limit)
        # print(self.repo_cursor.to_list())
        self.df = pd.DataFrame(self.repo_cursor.to_list())

    def data_transform(self):
        # self.df = self.df.where(self.df > 0, 1)
        # log.info(self.df.describe())
        # self.df = pd.DataFrame(np.log2(self.df), columns=self.df.columns, index=self.df.index)
        pass

if __name__ == '__main__':
    pcat = PCAT(timeout=40000)
    pcat.load_repo_statics(limit=0)
    pcat.data_transform()
    pcat.perform_pca(n_components=5)
    pass