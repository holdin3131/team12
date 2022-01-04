from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
from pymongo import MongoClient
import gridfs
import codecs
import certifi


app = Flask(__name__)

client = MongoClient('mongodb+srv://test:sparta@cluster0.5huhb.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=certifi.where())
db2 = client.db12team

SECRET_KEY = 'SPARTA'
fs = gridfs.GridFS(db2)
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


@app.route('/main')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db2.user.find_one({"id": payload['id']})
        img_name = list(db2.img_info.find({}))
        print(img_name)

        img_binaries = []

        for i in img_name:
            img_binary = fs.get(i['img'])
            # html 파일로 넘겨줄 수 있도록, base64 형태의 데이터로 변환
            base64_data = codecs.encode(img_binary.read(), 'base64')
            image = base64_data.decode('utf-8')
            img_binaries.append({'title':i['title'],'image':image,'writer':i['writer'],'description':i['description']})


        return render_template('main.html', username=user_info["username"], img=img_binaries )

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/main', methods = ["GET"])
def username_info():
    users_pic = list(db2.img_info.find({}, {'_id': False}))



    return jsonify({'users': users_pic})

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
        db2.last_login.insert_one({'id': id_receive})
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







@app.route('/')
def main():
    return render_template("login.html")


@app.route('/main')
def main_page():

    return render_template("main.html")




@app.route('/profile')
def edit_profile():
    return render_template("editprofile.html")


@app.route('/upload')
def img_upload():
    img_name = list(db2.img_info.find({}))[-1]
    img_binary = fs.get(img_name['img'])
    # html 파일로 넘겨줄 수 있도록, base64 형태의 데이터로 변환
    base64_data = codecs.encode(img_binary.read(), 'base64')
    image = base64_data.decode('utf-8')

    return render_template("upload.html", img = image)

# 방식2 : DB에 이미지 파일 자체를 올리는 방식
@app.route('/fileupload', methods=['POST'])
def file_upload():
    title_receive = request.form['title_give']
    file = request.files['file_give']
    # writer = list(db2.last_login.find({}))[-1]
    # gridfs 활용해서 이미지 분할 저장
    fs_image_id = fs.put(file)
    last_login = list(db2.last_login.find({}))[-1]
    writer = last_login['id']
    writer_id = db2.user.find_one({'id':writer})
    writer_name = writer_id['username']
    img_list = list(db2.img_info.find({}, {'_id': False}))
    count = len(img_list) + 1
    # db 추가
    doc = {
        'title': title_receive,
        'img': fs_image_id,
        'img_num': count,
        'writer':writer_name
    }
    # html 파일로 넘겨줄 수 있도록, base64 형태의 데이터로 변환
    db2.img_info.insert_one(doc)
    return jsonify({'result':'success'})

@app.route('/feedupload', methods=['POST'])
def feed_upload():
    last_img = list(db2.img_info.find({}))[-1]

    description = request.form['description_give']

    db2.img_info.update_one(last_img, {'$set': {'description': description}} )
    return jsonify({'result':'success'})
    return render_template("main.html")

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)