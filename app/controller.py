
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
        res_str = ""
        res_str += f'Maximal number of groups = {var_count["num_group"]}\n'
        res_str += f'Number of compatibility variables = {var_count["num_compat_var"]}\n'
        res_str += f'Number of constraints = {var_count["num_constraints"]}\n'
        res_str += "============ GROUPS ============\n"
        res_str += f'Number of groups {int(solver.Objective().Value())}\n'
        group_index = -1
        for pair_product_group in pair_product_group_list:
            if group_index != pair_product_group[1]:
                group_index = pair_product_group[1]
                res_str += f'\nGroupe {group_index} contains: {data["name_product"][pair_product_group[0]]}'
            else:
                res_str += f'{" " * len(str(group_index))}   {data["name_product"][pair_product_group[0]]}'

        self._view.setDisplayText(res_str)

    def _cancel_simu(self):
        self._view.clearDisplay()
        widget = self._view.form.itemAt(1)
        combo = widget.widget()

    def _connect_signals(self):
        self._view.buttons['Run'].clicked.connect(lambda: self._run_simu())
        self._view.buttons['Cancel'].clicked.connect(lambda: self._cancel_simu())
