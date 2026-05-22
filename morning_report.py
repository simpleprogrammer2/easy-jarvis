import datetime
from flask import Flask, jsonify
app = Flask(__name__)
def generate_morning_report():
    report = {'date': str(datetime.datetime.now())}
    return jsonify(report)
if __name__ == '__main__':
    app.run(debug=True)
