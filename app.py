from flask import Flask, render_template, jsonify, request, redirect, url_for
import datetime
import os
import sys
import traceback
from database import Survey, get_db, create_tables
from contextlib import contextmanager

app = Flask(__name__)

# 配置 Flask
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', '0') == '1'

# 打印环境信息
print("Python version:", sys.version)
print("Environment variables loaded:", bool(os.getenv('DATABASE_URL')))
print("Flask ENV:", os.getenv('FLASK_ENV'))
print("Current working directory:", os.getcwd())
print("Directory contents:", os.listdir())

try:
    # 确保数据库表已创建
    create_tables()
    print("Database tables created successfully")
except Exception as e:
    print(f"Error creating tables: {str(e)}")
    print("Traceback:", traceback.format_exc())

@contextmanager
def get_db_session():
    db = next(get_db())
    try:
        yield db
    except Exception as e:
        print(f"Database session error: {str(e)}")
        print("Traceback:", traceback.format_exc())
        raise
    finally:
        db.close()

@app.route('/')
def landing():
    try:
        return render_template('landing.html')
    except Exception as e:
        print(f"Error in landing route: {str(e)}")
        print("Traceback:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/detect')
def detect():
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error in detect route: {str(e)}")
        print("Traceback:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/get_time')
def get_time():
    try:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return jsonify({"time": current_time})
    except Exception as e:
        print(f"Error in get_time route: {str(e)}")
        print("Traceback:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/submit_survey', methods=['POST'])
def submit_survey():
    try:
        data = request.form.to_dict()
        print(f"Received survey data: {data}")
        
        with get_db_session() as db:
            survey = Survey(
                latitude=float(data.get('latitude', 0)),  # 从前端获取纬度
                longitude=float(data.get('longitude', 0)),  # 从前端获取经度
                noise_level=float(data.get('noise_level', 0)),  # 从前端获取噪声强度
                location_name=data.get('location_name', ''),  # 从前端获取位置名称
                result=data.get('result', ''),  # 问卷结果
                additional_info=data.get('additional_info', '')  # 额外信息
            )
            db.add(survey)
            db.commit()
            print("Survey data saved successfully")
        
        return redirect(url_for('thank_you'))
    except Exception as e:
        print(f"Error in submit_survey: {str(e)}")
        print("Traceback:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/thank_you')
def thank_you():
    try:
        return render_template('thank_you.html')
    except Exception as e:
        print(f"Error in thank_you route: {str(e)}")
        print("Traceback:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.errorhandler(500)
def handle_500(error):
    print(f"500 error occurred: {str(error)}")
    print("Traceback:", traceback.format_exc())
    return jsonify({
        "error": "Internal Server Error",
        "message": str(error),
        "traceback": traceback.format_exc()
    }), 500

@app.errorhandler(404)
def handle_404(error):
    print(f"404 error occurred: {str(error)}")
    return jsonify({
        "error": "Not Found",
        "message": str(error)
    }), 404

if __name__ == '__main__':
    app.run(debug=True) 