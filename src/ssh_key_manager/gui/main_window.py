import tkinter as tk
import re, os, json
from datetime import datetime
from tkinter import ttk, messagebox, simpledialog
from ssh_key_manager.core import key_manager, ssh_config
from ssh_key_manager.utils import validators
from ssh_key_manager.gui.dialogs import GenerateKeyDialog
from pathlib import Path
from PIL import Image, ImageTk

SETTINGS_PATH = os.path.expanduser("~/.ssh/ssh-gui-settings.json")

def log_to_file(msg: str):
    log_path = os.path.expanduser("~/.ssh/ssh-gui.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} — {msg}\n")


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        # иконка приложения
        icon_path = Path(__file__).parent.parent / "assets" / "ssh.png"
        if icon_path.exists():
            try:
                icon_img = ImageTk.PhotoImage(Image.open(icon_path))
                self.iconphoto(False, icon_img)
            except Exception as e:
                print(f"[WARNING] Не удалось установить иконку: {e}")

        self.title("SSH Key Manager")
        self.geometry("700x500")
        self.resizable(False, False)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        # вкладки
        self.keys_frame = ttk.Frame(self.notebook)
        self.config_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.keys_frame, text="Ключи")
        self.notebook.add(self.config_frame, text="Удаленные подключения")
        self.notebook.add(self.settings_frame, text="Настройки")
        # инициализация UI во вкладках
        self.load_settings()
        self.init_settings_tab()
        self.init_keys_tab()
        self.init_config_tab()


    def load_settings(self):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                settings = json.load(f)
        except Exception:
            settings = {}

        self.auto_copy_var = tk.BooleanVar(value=settings.get("auto_copy", True))
        self.log_to_file_var = tk.BooleanVar(value=settings.get("log_to_file", False))
        self.ssh_path_value = settings.get("ssh_path", "~/.ssh")

    def save_settings(self):
        settings = {
            "auto_copy": self.auto_copy_var.get(),
            "log_to_file": self.log_to_file_var.get(),
            "ssh_path": self.ssh_path_entry.get().strip()
        }
        try:
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Не удалось сохранить настройки: {e}")


    def init_keys_tab(self):
        # Список ключей
        self.keys_listbox = tk.Listbox(self.keys_frame, height=20)
        self.keys_listbox.pack(side="left", fill="y", padx=10, pady=10)

        scrollbar = tk.Scrollbar(self.keys_frame, orient="vertical")
        scrollbar.config(command=self.keys_listbox.yview)
        scrollbar.pack(side="left", fill="y")
        self.keys_listbox.config(yscrollcommand=scrollbar.set)

        self.keys_listbox.bind("<Double-1>", lambda e: self.show_public_key())

        # Панель действий (кнопки справа)
        button_frame = tk.Frame(self.keys_frame)
        button_frame.pack(side="left", fill="both", expand=True, padx=10)

        self.refresh_keys_btn = ttk.Button(button_frame, text="Обновить", command=self.refresh_keys)
        self.refresh_keys_btn.pack(pady=5)

        self.generate_btn = ttk.Button(button_frame, text="Добавить", command=self.generate_key_dialog)
        self.generate_btn.pack(pady=5)

        self.delete_btn = ttk.Button(button_frame, text="Удалить", command=self.delete_selected_key)
        self.delete_btn.pack(pady=5)

        self.view_btn = ttk.Button(button_frame, text="Показать публичный ключ", command=self.show_public_key)
        self.view_btn.pack(pady=5)

        self.refresh_keys()



    def init_config_tab(self):
        # Список хостов
        self.config_listbox = tk.Listbox(self.config_frame, height=20)
        self.config_listbox.pack(side="left", fill="y", padx=10, pady=10)

        scrollbar = tk.Scrollbar(self.config_frame, orient="vertical")
        scrollbar.config(command=self.config_listbox.yview)
        scrollbar.pack(side="left", fill="y")
        self.config_listbox.config(yscrollcommand=scrollbar.set)

        self.config_listbox.bind("<Double-1>", lambda e: self.edit_selected_host())

        # Панель кнопок
        button_frame = tk.Frame(self.config_frame)
        button_frame.pack(side="left", fill="both", expand=True, padx=10)

        ttk.Button(button_frame, text="Обновить", command=self.refresh_config_list).pack(pady=5)
        ttk.Button(button_frame, text="Добавить", command=self.add_host_dialog).pack(pady=5)
        ttk.Button(button_frame, text="Редактировать", command=self.edit_selected_host).pack(pady=5)
        ttk.Button(button_frame, text="Удалить", command=self.delete_selected_host).pack(pady=5)

        self.refresh_config_list()

    def refresh_config_list(self):
        self.config_listbox.delete(0, tk.END)
        all_blocks = ssh_config.read_config()
        self._config_entries = all_blocks

        if not all_blocks:
            # Файл пустой или не существует — показываем запись-заглушку
            self.config_listbox.insert(tk.END, "[Пустой конфиг — нажмите для редактирования]")
            self._config_entries = [{"type": "empty"}]  # специальный маркер
            return

        for i, entry in enumerate(all_blocks):
            if entry.get("type") == "host":
                display = f"Host {entry.get('host', '<без имени>')}"
            else:
                display = "[Глобальные настройки]"
            self.config_listbox.insert(tk.END, display)


    def get_selected_host_entry(self):
        try:
            index = self.config_listbox.curselection()[0]
            return self._config_entries[index]
        except IndexError:
            return None

    def delete_selected_host(self):
        entry = self.get_selected_host_entry()
        if not entry:
            messagebox.showwarning("Выбор хоста", "Выберите запись.")
            return

        if entry.get("type") != "host":
            messagebox.showinfo("Удаление", "Нельзя удалить глобальные настройки или пустой конфиг.")
            return

        host_name = entry.get("host")
        confirm = messagebox.askyesno("Удаление", f"Удалить Host '{host_name}'?")
        if confirm:
            ssh_config.delete_host(host_name)
            if self.log_to_file_var.get():
                log_to_file(f"Удалён хост: {host_name}")
            self.refresh_config_list()


    # открытие диалога добавления хоста
    def add_host_dialog(self):
        self._host_editor_dialog()


    def edit_selected_host(self):
        entry = self.get_selected_host_entry()
        if not entry:
            return

        if entry.get("type") == "empty":
            # открываем глобальный редактор (пустой)
            empty_entry = {"type": "global", "lines": []}
            self._config_entries = [empty_entry]
            self._global_editor_dialog(existing=empty_entry)
            return

        if entry.get("type") == "host":
            self._host_editor_dialog(existing={
                "Host": entry.get("host", ""),
                **entry.get("params", {})
            })
        elif entry.get("type") == "global":
            self._global_editor_dialog(existing=entry)

    def _host_editor_dialog(self, existing=None):
        # модальное окно редактирования записи
        dialog = tk.Toplevel(self)

        host_display = "<без имени>"
        if existing:
            host_display = existing.get("Host") or existing.get("host") or host_display
        else:
            host_display = "Новый"

        dialog.title(f"Хост: {host_display}")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()

        fields = ["Имя хоста", "Пользователь", "Порт", "Идентификационный файл"]
        entries = {}

        # поле Host (редактируемое только при добавлении)
        tk.Label(dialog, text="Host:").pack()
        host_entry = ttk.Entry(dialog)
        host_entry.pack(fill="x", padx=10)
        if existing:
            host_entry.insert(0, existing.get("Host"))
            host_entry.config(state="disabled")

        # поля (HostName, User, Port ...)
        for field in fields:
            tk.Label(dialog, text=field + ":").pack()
            e = ttk.Entry(dialog)
            e.pack(fill="x", padx=10)
            if existing and field in existing:
                e.insert(0, existing[field])
            entries[field] = e

        # сохранение
        def on_save():
            host = host_entry.get().strip()
            if not validators.is_valid_host_alias(host):
                messagebox.showerror("Ошибка", "Недопустимое имя Host.")
                return
            new_entry = {"Host": host}
            for k in fields:
                v = entries[k].get().strip()
                if v:
                    new_entry[k] = v
            ssh_config.add_or_update_host(new_entry)
            if self.log_to_file_var.get():
                log_to_file(f"Сохранён/обновлён хост: {host}")
            self.refresh_config_list()
            dialog.destroy()

        ttk.Button(dialog, text="Сохранить", command=on_save).pack(pady=10)

    def _global_editor_dialog(self, existing):
        dialog = tk.Toplevel(self)
        dialog.title("Глобальные настройки")
        dialog.geometry("600x475")
        dialog.transient(self)
        dialog.grab_set()

        text = tk.Text(dialog, wrap="none", font=("Courier", 10))
        text.pack(expand=True, fill="both", padx=10, pady=10)

        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=text.yview)
        scrollbar.pack(side="right", fill="y")
        text.configure(yscrollcommand=scrollbar.set)

        # вставка начального содержимого
        original_lines = existing.get("lines", [])
        text.insert("1.0", "".join(original_lines))

        # подсветка
        def highlight():
            text.tag_remove("keyword", "1.0", "end")
            text.tag_remove("comment", "1.0", "end")
            text.tag_remove("number", "1.0", "end")
            text.tag_remove("path", "1.0", "end")

            keywords = r"\b(ServerAliveInterval|ControlMaster|ControlPersist|User|Port|HostName|IdentityFile|ForwardAgent|ProxyJump)\b"
            for match in re.finditer(keywords, text.get("1.0", "end"), flags=re.IGNORECASE):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()} chars"
                text.tag_add("keyword", start, end)

            for match in re.finditer(r"#.*", text.get("1.0", "end")):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()} chars"
                text.tag_add("comment", start, end)

            for match in re.finditer(r"\b\d+\b", text.get("1.0", "end")):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()} chars"
                text.tag_add("number", start, end)

            for match in re.finditer(r"(~|/)[\w/\.-]+", text.get("1.0", "end")):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()} chars"
                text.tag_add("path", start, end)

        # конфигурация цветов
        text.tag_config("keyword", foreground="blue")
        text.tag_config("comment", foreground="gray")
        text.tag_config("number", foreground="darkgreen")
        text.tag_config("path", foreground="purple")

        # запуск подсветки при изменении текста
        def on_key_release(event):
            highlight()

        text.bind("<KeyRelease>", on_key_release)

        highlight()  # подсветить сразу

        def on_save():
            new_lines = text.get("1.0", "end").strip().splitlines(keepends=True)
            existing["lines"] = [line if line.endswith("\n") else line + "\n" for line in new_lines]
            ssh_config.write_config(self._config_entries)
            self.refresh_config_list()
            dialog.destroy()

        ttk.Button(dialog, text="Сохранить", command=on_save).pack(pady=10)



    """
    вкладка "Настройки"
    """
    def init_settings_tab(self):
        frame = self.settings_frame

        label = ttk.Label(frame, text="Настройки", font=("Helvetica", 12, "bold"))
        label.pack(pady=(20, 10))

        ttk.Checkbutton(frame, text="Автоматически копировать публичный ключ в буфер",
                        variable=self.auto_copy_var,
                        command=self.save_settings).pack(anchor="w", padx=20)

        ttk.Checkbutton(frame, text="Вести лог работы в файл ~/.ssh/ssh-gui.log",
                        variable=self.log_to_file_var,
                        command=self.save_settings).pack(anchor="w", padx=20)

        ttk.Label(frame, text="Путь к ssh (опционально):").pack(anchor="w", padx=20, pady=(20, 0))
        self.ssh_path_entry = ttk.Entry(frame)
        self.ssh_path_entry.insert(0, self.ssh_path_value)
        self.ssh_path_entry.pack(fill="x", padx=20)

        # сохранение поле пути
        self.ssh_path_entry.bind("<FocusOut>", lambda e: self.save_settings())


    """
    кнопки взаимодействия
    """
    def refresh_keys(self):
        self.keys_listbox.delete(0, tk.END)
        keys = key_manager.list_keys()
        for key in keys:
            self.keys_listbox.insert(tk.END, key)


    def get_selected_key(self):
        try:
            return self.keys_listbox.get(self.keys_listbox.curselection())
        except Exception:
            return None

    def delete_selected_key(self):
        key_name = self.get_selected_key()
        if not key_name:
            messagebox.showwarning("Выбор ключа", "Выберите ключ для удаления.")
            return

        confirm = messagebox.askyesno("Подтверждение", f"Удалить ключ '{key_name}'?")
        if confirm:
            success = key_manager.delete_keypair(key_name)
            if success:
                if self.log_to_file_var.get():
                    log_to_file(f"Удалён ключ: {key_name}")
                messagebox.showinfo("Готово", "Ключ удалён.")
                self.refresh_keys()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить ключ.")


    def show_public_key(self):
        key_name = self.get_selected_key()
        if not key_name:
            messagebox.showwarning("Выбор ключа", "Выберите ключ.")
            return

        pubkey = key_manager.get_public_key(key_name)
        if pubkey:
            if self.auto_copy_var.get():
                self.clipboard_clear()
                self.clipboard_append(pubkey)
                messagebox.showinfo("Публичный ключ", f"Ключ скопирован в буфер обмена:\n\n{pubkey}")
            else:
                messagebox.showinfo("Публичный ключ", f"{pubkey}")

            if self.log_to_file_var.get():
                log_to_file(f"Просмотрен публичный ключ: {key_name}")

    # открытие диалога генерации ключа
    def generate_key_dialog(self):
        GenerateKeyDialog(self, on_success=self.refresh_keys)