import tkinter as tk
from tkinter import ttk, messagebox
import data_access as dal
from business_logic import (
    AppointmentService,
    OrderService,
    SpecialistNotAvailableError,
    InsufficientStockError,
    ValidationError,
)


class TechRepairApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ремонт техники")
        self.root.geometry("700x500")

        self.appointment_service = AppointmentService()
        self.order_service = OrderService()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_appointments = ttk.Frame(self.notebook)
        self.tab_products = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_appointments, text="Запись на починку")
        self.notebook.add(self.tab_products, text="Товары")

        self.build_appointments_tab()
        self.build_products_tab()

        self.refresh_appointments()

    def build_appointments_tab(self):
        frame = ttk.Frame(self.tab_appointments, padding=10)
        frame.pack(fill="both", expand=True)

        form = ttk.LabelFrame(frame, text="Новая запись", padding=10)
        form.pack(fill="x", pady=5)

        ttk.Label(form, text="Техника:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.tech_combo = ttk.Combobox(form, state="readonly", width=25)
        self.tech_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Специалист:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.specialist_combo = ttk.Combobox(form, state="readonly", width=25)
        self.specialist_combo.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Дата и время (ГГГГ-ММ-ДД ЧЧ:ММ):").grid(
            row=1, column=0, sticky="w", padx=5, pady=5)
        self.datetime_entry = ttk.Entry(form, width=25)
        self.datetime_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(form, text="Записаться", command=self.on_book).grid(
            row=1, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

        table_frame = ttk.LabelFrame(frame, text="Список записей", padding=10)
        table_frame.pack(fill="both", expand=True, pady=5)

        columns = ("id", "tech", "specialist", "datetime")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col, title in zip(columns, ("ID", "Техника", "Специалист", "Дата и время")):
            self.tree.heading(col, text=title)
            self.tree.column(col, width=150)
        self.tree.pack(fill="both", expand=True)

        self.techs = dal.get_all_techs()
        self.specialists = dal.get_all_specialists()
        self.tech_combo["values"] = [t["name"] for t in self.techs]
        self.specialist_combo["values"] = [s["name"] for s in self.specialists]

    def on_book(self):
        tech_idx = self.tech_combo.current()
        spe_idx = self.specialist_combo.current()
        dt = self.datetime_entry.get().strip()

        if tech_idx == -1 or spe_idx == -1 or not dt:
            messagebox.showwarning("Внимание", "Заполните все поля")
            return

        tech_id = self.techs[tech_idx]["id"]
        specialist_id = self.specialists[spe_idx]["id"]

        try:
            self.appointment_service.book_appointment(tech_id, specialist_id, dt)
            messagebox.showinfo("Успех", "Запись создана")
            self.datetime_entry.delete(0, tk.END)
            self.refresh_appointments()
        except SpecialistNotAvailableError as e:
            messagebox.showerror("Занято", str(e))
        except ValidationError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неизвестная ошибка: {e}")

    def refresh_appointments(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for a in self.appointment_service.get_appointments():
            self.tree.insert("", "end", values=(
                a["id"], a["tech_name"], a["specialist_name"], a["datetime"]))

    def build_products_tab(self):
        frame = ttk.Frame(self.tab_products, padding=10)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Каталог товаров").pack(anchor="w")

        columns = ("id", "name", "price", "stock")
        self.products_tree = ttk.Treeview(frame, columns=columns, show="headings", height=8)
        for col, title in zip(columns, ("ID", "Название", "Цена", "На складе")):
            self.products_tree.heading(col, text=title)
            self.products_tree.column(col, width=150)
        self.products_tree.pack(fill="both", expand=False, pady=5)

        for p in dal.get_all_products():
            self.products_tree.insert("", "end", values=(
                p["id"], p["name"], p["price"], p["stock"]))

        order_frame = ttk.LabelFrame(frame, text="Оформить заказ", padding=10)
        order_frame.pack(fill="x", pady=10)

        ttk.Label(order_frame, text="ID товара:").grid(row=0, column=0, padx=5, pady=5)
        self.product_id_entry = ttk.Entry(order_frame, width=10)
        self.product_id_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(order_frame, text="Количество:").grid(row=0, column=2, padx=5, pady=5)
        self.qty_entry = ttk.Entry(order_frame, width=10)
        self.qty_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(order_frame, text="Рассчитать", command=self.on_order).grid(
            row=0, column=4, padx=10, pady=5)

        self.order_result = ttk.Label(frame, text="", font=("Arial", 11, "bold"))
        self.order_result.pack(anchor="w", pady=5)

    def on_order(self):
        try:
            product_id = int(self.product_id_entry.get())
            qty = int(self.qty_entry.get())
        except ValueError:
            messagebox.showerror("Ошибка", "ID и количество должны быть числами")
            return

        try:
            name, total = self.order_service.calculate_order(product_id, qty)
            self.order_result.config(text=f"Товар: {name} | Итого: {total: .2f} руб.")
        except InsufficientStockError as e:
            messagebox.showerror("Нет на складе", str(e))
        except ValidationError as e:
            messagebox.showerror("Ошибка", str(e))


def main() -> None:
    dal.init_db()  
    root = tk.Tk()
    app = TechRepairApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()