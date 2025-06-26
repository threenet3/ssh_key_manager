import tkinter as tk
from tkinter import ttk, messagebox
from core import key_manager
from utils import validators


class GenerateKeyDialog(tk.Toplevel):

    def __init__(self, parent, on_success=None):
        super().__init__(parent) # окно поверх главного
        self.title("Создание нового ключа")
        self.geometry("400x300")
        self.resizable(False, False)
        self.parent = parent
        self.on_success = on_success # при успешном создании ключа

        self.init_widgets()
        self.transient(parent) # вспомогательное, поверх главного
        self.grab_set() # модальное окно
        self.wait_window()


    """
    Создаем и размещаем все элементы 
    """
    def init_widgets(self):
        padx, pady = 10, 8

        # имя ключа
        tk.Label(self, text="Имя файла ключа:").pack(anchor="w", padx=padx, pady=(pady, 0))
        self.key_name_entry = ttk.Entry(self)
        self.key_name_entry.pack(fill="x", padx=padx)

        # комментарий
        tk.Label(self, text="Комментарий:").pack(anchor="w", padx=padx, pady=(pady, 0))
        self.comment_entry = ttk.Entry(self)
        self.comment_entry.pack(fill="x", padx=padx)



        # тип ключа (с выпадающим списком ed25519/rsa/ecdsa)
        tk.Label(self, text="Тип ключа:").pack(anchor="w", padx=padx, pady=(pady, 0))
        self.key_type_var = tk.StringVar(value="ed25519")
        self.type_combo = ttk.Combobox(self, textvariable=self.key_type_var, values=["ed25519", "rsa", "ECDSA"])
        self.type_combo.state(["readonly"]) # только выбор
        self.type_combo.pack(fill="x", padx=padx)


        # пароль (опционально)
        tk.Label(self, text="Пароль (опционально):").pack(anchor="w", padx=padx, pady=(pady, 0))
        self.pass_entry = ttk.Entry(self, show="*") # скрываем пароль
        self.pass_entry.pack(fill="x", padx=padx)

        # кнопки "создать" и "отмена"
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=pady)
        ttk.Button(button_frame, text="Создать", command=self.on_submit).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.destroy).pack(side="left", padx=5)


    """
    Обработчик нажатия "создать"
    """
    def on_submit(self):

        name = self.key_name_entry.get().strip()
        comment = self.comment_entry.get().strip()
        key_type = self.key_type_var.get()
        password = self.pass_entry.get()

        if not name:
            messagebox.showwarning("Ошибка", "Введите имя ключа.")
            return

        if not validators.is_valid_key_name(name):
            messagebox.showwarning("Ошибка", "Недопустимое или уже существующее имя ключа.")
            return

        # генерация ключа через key_manager
        success = key_manager.generate_keypair(
            key_name=name,
            key_type=key_type,
            passphrase=password,
            comment=comment
        )

        if success:
            messagebox.showinfo("Успешно", f"Ключ '{name}' создан.")
            if self.on_success:
                self.on_success() # вызов, чтобы обновить список
            self.destroy()
        else:
            messagebox.showerror("Ошибка", "Не удалось создать ключ.")
