from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
from pymongo import MongoClient
import gridfs
import codecs

app = Flask(__name__)
import certifi

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.5huhb.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=ca)
db = client.dbsparta
fs = gridfs.GridFS(db)

#################################
##  HTML을 주는 부분             ##
#################################

@app.route('/')
def main():
    return render_template("index.html")

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/profile')
def edit_profile():
    return render_template("editprofile.html")

@app.route('/upload')
def upload_page():
    img_info = list(db.camp2.find({}))[-1]
    img_binary = fs.get(img_info['img'])
    # html 파일로 넘겨줄 수 있도록, base64 형태의 데이터로 변환
    base64_data = codecs.encode(img_binary.read(), 'base64')
    image = base64_data.decode('utf-8')
    return render_template('upload.html',img=image)


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