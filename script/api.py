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

@app.route('/lang/nearby', methods=['GET'])
def lang_nearby():
    q = request.args.get('q')
    i = request.args.get('i', 10, type=int)
    l = request.args.get('l', 10, type=int)

    if i < 0:
        return jsonify({"error": "Invalid index"}), 400
    
    if not q:
        return jsonify({"error": "Missing query parameter 'q'"}), 400
    
    return jsonify(mango.user_nearby(q, i, l)), 200

@app.route('/<string:user>/rank', methods=['GET'])
def user_rank(user):
    return jsonify(mango.user_rank(username=user)), 200

@app.route('/<string:user>/lang/nearby', methods=['GET'])
def user_nearby(user):
    q = request.args.get('q')
    if not q:
        return jsonify({"error": "Missing query parameter 'q'"}), 400
    
    l = request.args.get('l', 10, type=int)
    if l < 0:
        return jsonify({"error": "Invalid limit"}), 400
    
    return jsonify(mango.user_nearby(q, None, l, user)), 200

@app.route('/<string:user>/repo_ranks', methods=['GET'])
def user_repo_ranks(user):
    return jsonify(mango.user_repo_ranks(user)), 200

@app.route('/search/user', methods=['GET'])
def search_user():
    # 从查询参数获取 q 的值
    q = request.args.get('q')
    l = request.args.get('l', 10, type=int)

    if not q:
        return jsonify({"error": "Missing query parameter 'q'"}), 400

    return jsonify(mango.user_search(q, l)), 200

@app.route('/search/lang', methods=['GET'])
def search_lang():
    q = request.args.get('q')
    l = request.args.get('l', 10, type=int)

    if not q:
        return jsonify({"error": "Missing query parameter 'q'"}), 400

    return jsonify(mango.language_search(q, l)), 200



if __name__ == '__main__':
    app.run(
        host='localhost',
        port=7000,
        debug=True
    )
