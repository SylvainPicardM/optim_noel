from PyQt5.QtWidgets import QTableWidgetItem

class AppController:
    def __init__(self, model, view):
        self._view = view
        self.model = model
        self._connect_signals()

    def _run_simu(self):
        widget = self._view.form.itemAt(1)
        combo = widget.widget()
        list_name = combo.currentData()
        solver, pair_product_group_list, data, var_count = self.model.run(list_name)
        group_index = -1
        group_dict = {}
        for pair_product_group in pair_product_group_list:
            if group_index != pair_product_group[1]:
                group_index = pair_product_group[1]
                p = data["name_product"][pair_product_group[0]]
                group_dict.setdefault(group_index, []).append(p)
            else:
                p = data["name_product"][pair_product_group[0]]
                group_dict[group_index].append(p)
        self._view.set_table(group_dict)

    def _cancel_simu(self):
        self._view.clear_table()
        widget = self._view.form.itemAt(1)
        combo = widget.widget()
        combo.clear()

    def _connect_signals(self):
        self._view.buttons['Run'].clicked.connect(lambda: self._run_simu())
        self._view.buttons['Cancel'].clicked.connect(lambda: self._cancel_simu())
