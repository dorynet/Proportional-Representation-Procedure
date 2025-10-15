import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk, END, CENTER, HORIZONTAL
import pandas as pd

import matplotlib
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.use('agg')

from math_functions import remainder_method, dHondt_rule, division_method, count_index, H_s_index, Ro_index


num_of_places_in = -1
parties_votes_in = pd.DataFrame()
current_results_df = pd.DataFrame()


quotas = [
        {"label": "Квота Хара (QH)", "value": "QH"},
        {"label": "Квота Друпа (QD)", "value": "QD"},
        {"label": "Нормальная имперская квота (QNI)", "value": "QNI"},
        {"label": "Усиленная имперская квота (QRI)", "value": "QRI"},
        ]
quotas_dict = pd.DataFrame(quotas).set_index('value').label.to_dict()
other_methods = [
        {"label": "Метод д'Онта (dHondt)", "value": "dHondt"},
        ]
other_methods_dict = pd.DataFrame(other_methods).set_index('value').label.to_dict()
divisor_methods = [
        {"label": "Метод наименьшего делителя, Метод Адамса (SD)", "value": "SD"},
        {"label": "Метод наибольшего делителя, метод Джефферсона (LD)", "value": "LD"},
        {"label": "Среднее арифметическое, Система Сент-Лаге, метод Уэбстера (AM)", "value": "AM"},
        {"label": "Среднее геометрическое, метод Хилла (GM)", "value": "GM"},
        {"label": "Среднее гармоническое, метод Дина (HM)", "value": "HM"},
        {"label": "Датская система (DS)", "value": "DS"},
        {"label": "Модифицированная система Сент-Лаге (MSL)", "value": "MSL"},
        ]
divisor_methods_dict = pd.DataFrame(divisor_methods).set_index('value').label.to_dict()
indexes = [
        {"label": "Максимальное отклонение (MD)", "value": "MD"},
        {"label": "Индекс Рэ (I)", "value": "I"},
        {"label": "Индекс Грофмана (G)", "value": "G"},
        {"label": "Индекс Лузмора-Хэнби (D)", "value": "D"},
        {"label": "Индекс удельного представительства (R)", "value": "R"},
        {"label": "Индекс Галлахера (LSq)", "value": "LSq"},
        {"label": "Обобщение индекса Галлахера (Hs)", "value": "Hs"},
        {"label": "Индекс представительности парламента, учитывающий неявку избирателей (ro)", "value": "ro"},
        ]
indexes_dict = pd.DataFrame(indexes).set_index('value').label.to_dict()


class PRMethodsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.title("Методы пропорционального представительства")
        self.geometry("1100x800")
        self._create_widgets()
        self._setup_table_styles()
        self.update_ui_state()

    def _setup_table_styles(self):
        style = ttk.Style()
        style.configure("Grid.Treeview", background="white", foreground="black", fieldbackground="white", borderwidth=1, relief="solid", rowheight=25)
        style.configure("Grid.Treeview.Heading", background="#f0f0f0", foreground="black", borderwidth=1, relief="solid", font=('Calibri', 10, 'bold'))
        style.map("Grid.Treeview", background=[('selected', '#CCE5FF')], foreground=[('selected', 'black')])
        style.layout("Grid.Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

    def _create_widgets(self):
        self.master_scroll_frame = ctk.CTkScrollableFrame(self, label_text="", fg_color="transparent")
        self.master_scroll_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        self.master_scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.header_frame = ctk.CTkFrame(self.master_scroll_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="ew") # Убрали внешний pady
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.header_label = ctk.CTkLabel(self.header_frame, text="Процедура пропорционального представительства", font=ctk.CTkFont(size=20, weight="bold"))
        self.header_label.grid(row=0, column=0, sticky="ew")

        # Основная панель управления и данных
        self.main_frame = ctk.CTkFrame(self.master_scroll_frame, fg_color="#f0f0f0")
        self.main_frame.grid(row=1, column=0, padx=10, pady=0, sticky="nsew") 

        
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=0)
        self.main_frame.grid_rowconfigure(6, weight=1) 
        
        self.load_data_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.load_data_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.load_data_frame.grid_columnconfigure(0, weight=1)
        self.load_button = ctk.CTkButton(self.load_data_frame, text="Загрузить данные (CSV)", command=self.load_data)
        self.load_button.grid(row=0, column=0, sticky="ew")

        # --- Ввод количества мест ---
        self.num_places_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.num_places_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.num_places_frame.grid_columnconfigure(1, weight=1)
        self.num_places_label = ctk.CTkLabel(self.num_places_frame, text="Введите количество мест в парламенте:")
        self.num_places_label.grid(row=0, column=0, padx=(0, 5))
        self.num_places_entry = ctk.CTkEntry(self.num_places_frame, placeholder_text="Например: 100", width=150)
        self.num_places_entry.grid(row=0, column=1, sticky="w")
        self.num_places_entry.bind("<KeyRelease>", self.on_num_places_change)

        # --- SCROLLABLE FRAME для методов ---
        self.methods_scroll_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent", height=250, orientation="horizontal")
        self.methods_scroll_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.methods_frame = ctk.CTkFrame(self.methods_scroll_frame, fg_color="transparent")
        self.methods_frame.pack(fill="both", expand=True)
        self.methods_frame.grid_columnconfigure((0,1,2), weight=1, minsize=300)
        # ... методы ...
        self.reminder_methods_label = ctk.CTkLabel(self.methods_frame, text="Методы наибольшего остатка:", font=ctk.CTkFont(weight="bold"))
        self.reminder_methods_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.reminder_checkboxes = []
        for i, quota in enumerate(quotas):
            checkbox = ctk.CTkCheckBox(self.methods_frame, text=quota["label"], corner_radius=6, hover=True)
            checkbox.grid(row=i+1, column=0, padx=10, pady=2, sticky="w")
            self.reminder_checkboxes.append(checkbox)
        self.other_methods_label = ctk.CTkLabel(self.methods_frame, text="Метод наибольшего среднего:", font=ctk.CTkFont(weight="bold"))
        self.other_methods_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.other_checkboxes = []
        for i, method in enumerate(other_methods):
            checkbox = ctk.CTkCheckBox(self.methods_frame, text=method["label"], corner_radius=6, hover=True)
            checkbox.grid(row=i+1, column=1, padx=10, pady=2, sticky="w")
            self.other_checkboxes.append(checkbox)
        self.divisor_methods_label = ctk.CTkLabel(self.methods_frame, text="Методы делителей:", font=ctk.CTkFont(weight="bold"))
        self.divisor_methods_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.divisor_checkboxes = []
        for i, method in enumerate(divisor_methods):
            checkbox = ctk.CTkCheckBox(self.methods_frame, text=method["label"], corner_radius=6, hover=True)
            checkbox.grid(row=i+1, column=2, padx=10, pady=2, sticky="w")
            self.divisor_checkboxes.append(checkbox)

        # --- Фрейм для индексов ---
        self.indexes_setup_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.indexes_setup_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.indexes_label = ctk.CTkLabel(self.indexes_setup_frame, text="Индексы представительности:", font=ctk.CTkFont(weight="bold"))
        self.indexes_label.grid(row=0, column=0, columnspan=5, padx=5, pady=5, sticky="w")
        self.index_checkboxes = {}
        num_indexes = len(indexes)
        mid_point = (num_indexes + 1) // 2
        col_offset = 0
        for i, index in enumerate(indexes):
            row = i % mid_point + 1
            if i >= mid_point:
                col_offset = 5
            checkbox = ctk.CTkCheckBox(self.indexes_setup_frame, text=index["label"], corner_radius=6, hover=True)
            checkbox.grid(row=row, column=col_offset, padx=10, pady=2, sticky="w")
            self.index_checkboxes[index["value"]] = checkbox
            if index["value"] == "Hs":
                hs_s_label = ctk.CTkLabel(self.indexes_setup_frame, text="s:")
                hs_s_label.grid(row=row, column=col_offset + 1, padx=(0, 2), pady=2, sticky="w")
                self.hs_s_entry = ctk.CTkEntry(self.indexes_setup_frame, width=50, placeholder_text="2")
                self.hs_s_entry.grid(row=row, column=col_offset + 2, padx=(0, 10), pady=2, sticky="w")
                self.hs_s_entry.insert(0, "2")
            if index["value"] == "ro":
                ro_nu_label = ctk.CTkLabel(self.indexes_setup_frame, text="ν (неявка):")
                ro_nu_label.grid(row=row, column=col_offset + 1, padx=(0, 2), pady=2, sticky="w")
                self.ro_nu_entry = ctk.CTkEntry(self.indexes_setup_frame, width=50, placeholder_text="0.3")
                self.ro_nu_entry.grid(row=row, column=col_offset + 2, padx=(0, 5), pady=2, sticky="w")
                self.ro_nu_entry.insert(0, "0.3")
                ro_alpha_label = ctk.CTkLabel(self.indexes_setup_frame, text="α (против всех):")
                ro_alpha_label.grid(row=row, column=col_offset + 3, padx=(0, 2), pady=2, sticky="w")
                self.ro_alpha_entry = ctk.CTkEntry(self.indexes_setup_frame, width=50, placeholder_text="0.05")
                self.ro_alpha_entry.grid(row=row, column=col_offset + 4, padx=0, pady=2, sticky="w")
                self.ro_alpha_entry.insert(0, "0.05")
        
        # --- Кнопка расчета ---
        self.calculate_button = ctk.CTkButton(self.main_frame, text="Рассчитать и показать результаты", command=self.calculate_results)
        self.calculate_button.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        
        # --- Кнопки управления результатами ---
        self.results_control_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.results_control_frame.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        self.results_control_frame.grid_columnconfigure(0, weight=1)
        self.download_button = ctk.CTkButton(self.results_control_frame, text="Скачать результаты (CSV)", command=self.download_results, state=ctk.DISABLED)
        self.download_button.grid(row=0, column=0, sticky="ew")

        # --- Отображение результатов (таблица) ---
        self.results_frame = ctk.CTkFrame(self.main_frame, fg_color="#ffffff")
        self.results_frame.grid(row=6, column=0, padx=10, pady=10, sticky="nsew")
        self.results_frame.grid_columnconfigure(0, weight=1)
        self.results_frame.grid_rowconfigure(0, weight=1)
        self.placeholder_label = ctk.CTkLabel(self.results_frame, text="Загрузите данные и укажите количество мест, затем нажмите 'Рассчитать'.", text_color="#888888")
        self.placeholder_label.grid(row=0, column=0, sticky="nsew")
        self.tree = None
        self.fixed_tree = None

    
    def update_ui_state(self):
        
        data_loaded = not parties_votes_in.empty
        num_places_entered = self.num_places_entry.get().isdigit() and int(self.num_places_entry.get()) > 0
        state = ctk.NORMAL if data_loaded else ctk.DISABLED
        calc_button_state = ctk.NORMAL if data_loaded and num_places_entered else ctk.DISABLED
        self.num_places_entry.configure(state=state)
        self.calculate_button.configure(state=calc_button_state)
        for cb in self.reminder_checkboxes + self.other_checkboxes + self.divisor_checkboxes:
            cb.configure(state=state)
        all_index_widgets = list(self.index_checkboxes.values()) + [
            self.hs_s_entry, self.ro_nu_entry, self.ro_alpha_entry
        ]
        for widget in all_index_widgets:
            widget.configure(state=state)

    def load_data(self):
        
        filepath = filedialog.askopenfilename(filetypes=(("CSV files", "*.csv"), ("all files", "*.*")))
        if not filepath: return
        try:
            global parties_votes_in
            parties_votes_in = pd.read_csv(filepath)
            if 'Party' not in parties_votes_in.columns or 'Votes' not in parties_votes_in.columns:
                messagebox.showerror("Ошибка загрузки", "CSV файл должен содержать колонки 'Party' и 'Votes'.")
                parties_votes_in = pd.DataFrame()
                self.update_ui_state()
                return
            parties_votes_in['Votes'] = pd.to_numeric(parties_votes_in['Votes'], errors='coerce')
            parties_votes_in.dropna(subset=['Votes'], inplace=True)
            messagebox.showinfo("Успех", f"Данные успешно загружены из:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить файл: {e}")
            parties_votes_in = pd.DataFrame()
        self.clear_results_table()
        self.update_ui_state()

    def on_num_places_change(self, event=None):
        
        global num_of_places_in
        entry_value = self.num_places_entry.get()
        num_of_places_in = int(entry_value) if entry_value.isdigit() else -1
        self.update_ui_state()

    def calculate_results(self):
        
        global parties_votes_in, num_of_places_in, current_results_df
        if parties_votes_in.empty: messagebox.showwarning("Предупреждение", "Сначала загрузите данные."); return
        if num_of_places_in <= 0: messagebox.showwarning("Предупреждение", "Введите корректное положительное количество мест."); return
        selected_methods = []
        for cb in self.reminder_checkboxes:
            if cb.get():
                label_text = cb.cget("text")
                for option in quotas:
                    if option["label"] == label_text: selected_methods.append(option["value"]); break
        for cb in self.other_checkboxes:
            if cb.get():
                label_text = cb.cget("text")
                for option in other_methods:
                    if option["label"] == label_text: selected_methods.append(option["value"]); break
        for cb in self.divisor_checkboxes:
            if cb.get():
                label_text = cb.cget("text")
                for option in divisor_methods:
                    if option["label"] == label_text: selected_methods.append(option["value"]); break
        if not selected_methods: messagebox.showwarning("Предупреждение", "Выберите хотя бы один метод пропорционального представительства."); return
        selected_indexes = [key for key, cb in self.index_checkboxes.items() if cb.get()]
        s, nu, alpha = None, None, None
        try:
            if 'Hs' in selected_indexes:
                s = float(self.hs_s_entry.get())
            if 'ro' in selected_indexes:
                nu = float(self.ro_nu_entry.get())
                alpha = float(self.ro_alpha_entry.get())
                if not (0 <= nu <= 1 and 0 <= alpha <= 1):
                    messagebox.showerror("Ошибка", "Значения ν (неявка) и α (против всех) должны быть от 0 до 1.")
                    return
        except ValueError:
            messagebox.showerror("Ошибка", "Параметры для индексов (s, ν, α) должны быть числами.")
            return
        parties_places_table = parties_votes_in.copy()
        for method_key in selected_methods:
            method_name_display, result_places = "", None
            if method_key in quotas_dict:
                method_name_display = quotas_dict[method_key]
                result_places = remainder_method(parties_votes_in, method_key, num_of_places_in)
            elif method_key in other_methods_dict:
                method_name_display = other_methods_dict[method_key]
                result_places = dHondt_rule(parties_votes_in, num_of_places_in)
            elif method_key in divisor_methods_dict:
                method_name_display = divisor_methods_dict[method_key]
                result_places = division_method(parties_votes_in, method_key, num_of_places_in)
            if result_places is not None:
                parties_places_table[method_name_display] = result_places
        index_rows_data = []
        if selected_indexes:
            method_columns = [col for col in parties_places_table.columns if col not in ['Party', 'Votes']]
            for index_key in selected_indexes:
                index_label = indexes_dict[index_key]
                row_data = {'Party': index_label, 'Votes': ''}
                for method_col in method_columns:
                    temp_df = parties_votes_in[['Party', 'Votes']].copy()
                    temp_df['Places'] = parties_places_table[method_col]
                    index_value = None
                    if index_key == 'Hs':
                        index_value = H_s_index(temp_df, s)
                    elif index_key == 'ro':
                        index_value = Ro_index(temp_df, nu, alpha)
                    else:
                        index_value = count_index(temp_df, index_key)
                    row_data[method_col] = f"{index_value:.4f}"
                index_rows_data.append(row_data)
        if index_rows_data:
            index_df = pd.DataFrame(index_rows_data)
            spacer_row = pd.DataFrame([['-'*20, ''] + ['-'*15] * (len(parties_places_table.columns) - 2)], columns=parties_places_table.columns)
            final_df = pd.concat([parties_places_table, spacer_row, index_df], ignore_index=True)
        else:
            final_df = parties_places_table
        current_results_df = final_df.copy()
        self.display_results_table(final_df)
        self.download_button.configure(state=ctk.NORMAL)

    def download_results(self):
        
        global current_results_df
        if current_results_df.empty: messagebox.showwarning("Предупреждение", "Нет результатов для скачивания."); return
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")], initialfile="voting_results.csv")
        if filepath:
            try:
                current_results_df.to_csv(filepath, index=False, encoding='utf-8-sig')
                messagebox.showinfo("Успех", f"Результаты успешно сохранены в:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def display_results_table(self, data_df: pd.DataFrame):
        self.clear_results_table()

        
        self.results_frame.grid_rowconfigure(0, weight=1) # Строка для таблицы растягивается
        self.results_frame.grid_rowconfigure(1, weight=0) # Строка для скроллбара
        self.results_frame.grid_columnconfigure(0, weight=1)

        # Создаем основной контейнер с рамкой, он теперь будет в row=0
        table_container_frame = ctk.CTkFrame(self.results_frame, fg_color="#ffffff", border_width=1, border_color="#cccccc")
        table_container_frame.grid(row=0, column=0, sticky="nsew") # Убраны padx/pady, они будут у родителя
        table_container_frame.grid_columnconfigure(1, weight=1)
        table_container_frame.grid_rowconfigure(0, weight=1)

        # Контейнер для закрепленного столбца
        fixed_container = ctk.CTkFrame(table_container_frame, fg_color="#ffffff")
        fixed_container.grid(row=0, column=0, sticky="nsw", padx=(1,0))
        fixed_container.grid_rowconfigure(0, weight=1)

        # Создаем Treeview для первого столбца с сеткой 
        first_col = data_df.columns[0]
        self.fixed_tree = ttk.Treeview(fixed_container, columns=[first_col], show='headings', style="Grid.Treeview")
        self.fixed_tree.heading(first_col, text=first_col)
        self.fixed_tree.column(first_col, anchor='w', width=200)
        self.fixed_tree.tag_configure('oddrow', background='white')
        self.fixed_tree.tag_configure('evenrow', background='#f8f8f8')
        for index, row in data_df.iterrows():
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.fixed_tree.insert("", END, values=[row[first_col]], tags=(tag,))
        self.fixed_tree.grid(row=0, column=0, sticky="nsew")

        # Контейнер для прокручиваемой таблицы
        scrollable_container = ctk.CTkFrame(table_container_frame, fg_color="#ffffff")
        scrollable_container.grid(row=0, column=1, sticky="nsew")
        scrollable_container.grid_columnconfigure(0, weight=1)
        scrollable_container.grid_rowconfigure(0, weight=1)

        # Создаем Treeview для остальных столбцов с сеткой 
        remaining_cols = data_df.columns[1:].tolist()
        self.tree = ttk.Treeview(scrollable_container, columns=remaining_cols, show='headings', style="Grid.Treeview")
        for col in remaining_cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor=CENTER, width=max(120, len(col) * 9))
        self.tree.tag_configure('oddrow', background='white')
        self.tree.tag_configure('evenrow', background='#f8f8f8')
        for index, row in data_df.iterrows():
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.tree.insert("", END, values=row[1:].tolist(), tags=(tag,))
        self.tree.grid(row=0, column=0, sticky="nsew")

        
        self.hsb = ctk.CTkScrollbar(self.results_frame, orientation=HORIZONTAL, command=self.tree.xview)
        self.hsb.grid(row=1, column=0, sticky="ew", pady=(5, 0))

        # Связываем скроллбар с таблицей
        self.tree.configure(xscrollcommand=self.hsb.set)

        # Общий вертикальный скроллбар 
        self.vsb = ctk.CTkScrollbar(table_container_frame, command=self.on_vsb_move)
        self.vsb.grid(row=0, column=2, sticky="ns")
        self.tree.configure(yscrollcommand=self.on_tree_scroll)
        self.fixed_tree.configure(yscrollcommand=self.on_fixed_tree_scroll)

        # Привязка событий 
        self.tree.bind("<MouseWheel>", self.on_mousewheel)
        self.fixed_tree.bind("<MouseWheel>", self.on_mousewheel)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select, "+")
        self.fixed_tree.bind("<<TreeviewSelect>>", self.on_fixed_tree_select, "+")

    def on_tree_select(self, event):
        if not self.tree.selection(): return
        item = self.tree.selection()[0]
        self.fixed_tree.selection_set(self.fixed_tree.get_children()[self.tree.index(item)])

    def on_fixed_tree_select(self, event):
        if not self.fixed_tree.selection(): return
        item = self.fixed_tree.selection()[0]
        self.tree.selection_set(self.tree.get_children()[self.fixed_tree.index(item)])

    def on_vsb_move(self, *args):
        self.tree.yview(*args)
        self.fixed_tree.yview(*args)

    def on_tree_scroll(self, first, last):
        self.fixed_tree.yview_moveto(first)
        self.vsb.set(first, last)

    def on_fixed_tree_scroll(self, first, last):
        self.tree.yview_moveto(first)
        self.vsb.set(first, last)

    def on_mousewheel(self, event):
        self.tree.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.fixed_tree.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def clear_results_table(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        self.placeholder_label = ctk.CTkLabel(self.results_frame, text="Результаты будут отображены здесь.", text_color="#888888")
        self.placeholder_label.grid(row=0, column=0, sticky="nsew")

    def run(self):
        self.mainloop()

if __name__ == "__main__":
    app = PRMethodsApp()
    app.run()