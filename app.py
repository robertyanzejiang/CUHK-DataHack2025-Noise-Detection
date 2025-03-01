from flask import Flask, render_template, jsonify, request, redirect, url_for
import datetime
from database import Survey, get_db, create_tables
from contextlib import contextmanager
import os

app = Flask(__name__)

# 打印环境变量（不包含敏感信息）
print("Environment variables loaded:", bool(os.getenv('DATABASE_URL')))
print("Flask ENV:", os.getenv('FLASK_ENV'))

try:
    # 确保数据库表已创建
    create_tables()
    print("Database tables created successfully")
except Exception as e:
    print(f"Error creating tables: {e}")

@contextmanager
def get_db_session():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/detect')
def detect():
    return render_template('index.html')

@app.route('/get_time')
def get_time():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({"time": current_time})

@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    try:
        data = request.form.to_dict()
        
        with get_db_session() as db:
            survey = Survey(
                result=data.get('result', ''),
                additional_info=data.get('additional_info', '')
            )
            db.add(survey)
            db.commit()
        
        return redirect(url_for('thank_you'))
    except Exception as e:
        print(f"Error in submit_survey: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

@app.errorhandler(500)
def handle_500(error):
    return jsonify({
        "error": "Internal Server Error",
        "message": str(error)
    }), 500

if __name__ == '__main__':
    app.run(debug=True) 