import csv
import os
from flask import current_app


class Report:
    def generate(self, data):
        csv = current_app.config['REPORT_FOLDER'] + 'Report.csv'
        with open(csv, 'w+') as file:
            writer = csv.writer(file)
            writer.writerow(data)
        file.close()

