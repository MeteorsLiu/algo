import os
from flask import Flask, jsonify
from dotenv import load_dotenv

# 方法一
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src import rank

load_dotenv()

GITHUB_ACCESS_TOKEN = os.environ.get('GITHUB_ACCESS_TOKEN')

app = Flask(__name__)

@app.route('/<string:user>/rank', methods=['GET'])
def user_handle(user):
    rank_avg = rank.user_rank(
        username=user,
        token=GITHUB_ACCESS_TOKEN
    )

    return jsonify({'rank_avg': rank_avg}), 200

if __name__ == '__main__':
    app.run(debug=True)
