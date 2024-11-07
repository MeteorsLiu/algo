import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from flask_cors import CORS  # 导入 CORS

# 方法一
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src import rank, mangodb

mango = mangodb.Mangodb()

load_dotenv()

GITHUB_ACCESS_TOKEN = os.environ.get('GITHUB_ACCESS_TOKEN')

app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})  # 允许所有跨域请求
CORS(app, resources=r'/*')

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Welcome to the API!'}), 200

@app.route('/<string:user>/rank', methods=['GET'])
def user_handle(user):
    rank_avg = rank.user_rank(
        username=user,
        token=GITHUB_ACCESS_TOKEN
    )

    return jsonify({'rank_avg': rank_avg}), 200

@app.route('/search', methods=['GET'])
def search():
    # 从查询参数获取 q 的值
    q = request.args.get('q')

    if not q:
        return jsonify({"error": "Missing query parameter 'q'"}), 400

    return jsonify(mango.user_search(q)), 200

if __name__ == '__main__':
    app.run(
        host='localhost',
        port=7000,
        debug=True
    )
