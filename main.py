from flask import Flask, request, render_template, send_file
import re
import pandas as pd
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def process_log_file(file_path):
    pattern = r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"

    ip_addrs_lst = []
    failed_lst = []
    success_lst = []

    with open(file_path, "r") as logfile:
        for log in logfile:
            ip_add = re.search(pattern, log)
            if ip_add:
                ip_addrs_lst.append(ip_add.group())
                lst = log.split(" ")
                try:
                    failed_lst.append(int(lst[-1]))
                    success_lst.append(int(lst[-4]))
                except ValueError:
                    continue

    total_failed = sum(failed_lst)
    total_success = sum(success_lst)
    ip_addrs_lst.append("Total")
    success_lst.append(total_success)
    failed_lst.append(total_failed)

    df = pd.DataFrame(columns=['IP Address', "Success", "Failed"])
    df['IP Address'] = ip_addrs_lst
    df["Success"] = success_lst
    df["Failed"] = failed_lst

    output_csv = os.path.join(os.getcwd(), "output.csv")
    df.to_csv(output_csv, index=False)
    
    return output_csv

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        file_path = os.path.join(os.getcwd(), file.filename)
        file.save(file_path)
        try:
            output_csv = process_log_file(file_path)
            return send_file(output_csv, as_attachment=True)
        except Exception as e:
            logging.error("Error processing file: %s", e)
            return str(e)

if __name__ == '__main__':
    app.run(debug=True)
