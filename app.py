from flask import Flask, render_template, jsonify, request, redirect, url_for
import datetime
from database import Survey, get_db, create_tables
from contextlib import contextmanager

app = Flask(__name__)

# 确保数据库表已创建
create_tables()

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
    data = request.form.to_dict()
    
    with get_db_session() as db:
        survey = Survey(
            result=data.get('result', ''),
            additional_info=data.get('additional_info', '')
        )
        db.add(survey)
        db.commit()
    
    return redirect(url_for('thank_you'))

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

if __name__ == '__main__':
    app.run(debug=True) 