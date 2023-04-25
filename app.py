import json
import os
from flask import Flask, render_template, g, request, jsonify, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import sqlite3

app = Flask(__name__)
# 解决中文乱码
app.config['JSON_AS_ASCII'] = False
DB_INIFILE = os.path.join(os.getcwd(), "db/shcema.sql")
DATABASE = os.path.join(os.getcwd(), "data.db")

# 连接数据库
def connect_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = sqlite3.connect(DATABASE)
    return db

# 数据库初始化，运行的时候在python console里要用
def init_db():
    print(".sql file path:{}".format(DB_INIFILE))
    with app.app_context():
        db = connect_db()
        with app.open_resource(DB_INIFILE, mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def close_db(exception):
    if hasattr(g, 'db'):
        g.db.close()

# 插入数据库
def insertUser(id, pwd):
    sql = "insert into user_info values(?, ?)"
    conn = g.db
    cursor = conn.cursor()
    try:
        cursor.execute(sql, (id, pwd))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise TypeError("insert error:{}".format(e))    # 抛出异常

"""——————————————————————————————
            API: 用户登录
————————————————————————————————"""
@app.route('/login', methods=['POST', 'GET'])
def user_login():
    if request.method == 'POST':
        username = request.form.get("id")
        pwd = request.form.get("pwd")
        print(pwd)
        # 2、处理请求参数缺少
        if not all([username, pwd]):
            flash('缺少请求参数')
            return redirect(url_for('login'))
        # 3、验证账号密码
        conn = g.db
        cursor = conn.cursor()
        query = "SELECT * FROM user_info WHERE usr_id=? AND usr_pwd=?"
        cursor.execute(query, (username, pwd))
        if not cursor.fetchone():
            print("登录失败")
            return 'NO'
        else:
            print("登录成功")
            return 'OK'
        conn.close()

"""——————————————————————————————
            API: 根据年龄查询学生
————————————————————————————————"""
@app.route('/search', methods=['POST'])
def search_by_age():
    age = request.form.get("age")
    print(age)
    # 处理请求参数缺失
    if not age:
        flash('缺少请求参数')
        return redirect(url_for('search'))
    # 根据年龄查询学生
    conn = g.db
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_info WHERE age=" + age)
    rows = cursor.fetchall()
    if rows:
        data = []
        for row in rows:
            item = {"name": row[0], "age": row[1], "class": row[2], "height": row[3], "weight": row[4]}
            data.append(item)
        print(data)
        return jsonify(data)
    else:
        print("无此年龄的学生")
        return 'NO'
    conn.close()

@app.route("/home")
def gotoHome():
    return render_template('home.html')


@app.route("/")
def root():
    """
    登录页
    :return: index.html
    """
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port='5000')

