from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
from pymongo import MongoClient
import gridfs
import codecs
import certifi


app = Flask(__name__)

client = MongoClient('mongodb+srv://test:sparta@cluster0.dik82.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=certifi.where())
db2 = client.db12team

SECRET_KEY = 'SPARTA'
import jwt
import datetime
import hashlib

# token확인 함수
def check_token():
    # 현재 이용자의 컴퓨터에 저장된 cookie 에서 mytoken 을 가져옵니다.
    token_receive = request.cookies.get('mytoken')
    # token을 decode하여 payload를 가져오고, payload 안에 담긴 유저 id를 통해 DB에서 유저의 정보를 가져옵니다.
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    return db.user.find_one({'id': payload['id']}, {'_id': False})


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db2.user.find_one({"id": payload['id']})
        return render_template('main(example).html', username=user_info["username"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/api/register', methods=['POST'])
def api_signup():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    fullname_receive = request.form['fullname_give']
    username_receive = request.form['username_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db2.user.insert_one({'id': id_receive, 'pw': pw_hash, 'fullname': fullname_receive, 'username': username_receive})

    return jsonify({'result': 'success'})


@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db2.user.find_one({'id': id_receive, 'pw': pw_hash})
    if result is not None:
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1500)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/api/username', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')

    try:

        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        print(payload)

        userinfo = db2.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'username': userinfo['username']})
    except jwt.ExpiredSignatureError:

        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다.'})




#################################
##  HTML을 주는 부분             ##
#################################

client = MongoClient('mongodb+srv://test:sparta@cluster0.5huhb.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=certifi.where())
db = client.dbsparta
fs = gridfs.GridFS(db)


@app.route('/')
def main():
    return render_template("index.html")


@app.route('/main')
def main_page():
    return render_template("main.html")



@app.route('/profile')
def edit_profile():
    return render_template("editprofile.html")

@app.route('/upload')
def upload():
    return render_template("upload.html")

# @app.route('/upload')
# def upload_page():
#     img_info = list(db.camp2.find({}))[-1]
#     img_binary = fs.get(img_info['img'])
#     # html 파일로 넘겨줄 수 있도록, base64 형태의 데이터로 변환
#     base64_data = codecs.encode(img_binary.read(), 'base64')
#     image = base64_data.decode('utf-8')
#     return render_template('upload.html',img=image)


# 방식2 : DB에 이미지 파일 자체를 올리는 방식
@app.route('/fileupload', methods=['POST'])
def file_upload():
    title_receive = request.form['title_give']
    file = request.files['file_give']
    # gridfs 활용해서 이미지 분할 저장
    fs_image_id = fs.put(file)

    # db 추가
    doc = {
        'title': title_receive,
        'img': fs_image_id
    }
    db.camp2.insert_one(doc)

    return jsonify({'result':'success'})

# 주소에다가 /fileshow/이미지타이틀 입력하면 그 이미지타이틀을 title이라는 변수로 받아옴
@app.route('/fileshow/<title>')
def file_show(title):
    # title은 현재 이미지타이틀이므로, 그것을 이용해서 db에서 이미지 '파일'을 가지고 옴
    img_info = db.camp2.find_one({'title': title})
    img_binary = fs.get(img_info['img'])
    # html 파일로 넘겨줄 수 있도록, base64 형태의 데이터로 변환
    base64_data = codecs.encode(img_binary.read(), 'base64')
    image = base64_data.decode('utf-8')
    # 해당 이미지의 데이터를 jinja 형식으로 사용하기 위해 넘김
    return render_template('showimg.html', img=image)

# @app.route('/')
# def file_show2():
#     # title은 현재 이미지타이틀이므로, 그것을 이용해서 db에서 이미지 '파일'을 가지고 옴
#     img_info = list(db.camp2.find({}))[-1]
#     img_binary = fs.get(img_info['img'])
#     # html 파일로 넘겨줄 수 있도록, base64 형태의 데이터로 변환
#     base64_data = codecs.encode(img_binary.read(), 'base64')
#     image = base64_data.decode('utf-8')
#     # 해당 이미지의 데이터를 jinja 형식으로 사용하기 위해 넘김
#     return render_template('index.html', img=image)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)