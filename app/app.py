import sys
from PyQt5.QtWidgets import QApplication
from view import AppView
from controller import AppController
from model import AppModel
import pandas as pd

def create_complete_data(csv_path):
    df = pd.read_csv(csv_path, sep=",")
    return df.values, df.columns.to_list(), df

def main():
    retention_csv = 'data/retention_pc.csv'
    compat_matrix, products, df = create_complete_data(retention_csv)
    app = QApplication(sys.argv)
    view = AppView(products=products)
    view.show()
    model = AppModel(compat_matrix, products)
    AppController(view=view, model=model)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()