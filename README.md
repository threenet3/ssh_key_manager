# SSH Key Manager

**Графическая утилита для управления SSH-ключами** на Python с использованием Tkinter. Позволяет создавать, удалять, просматривать и назначать SSH-ключи, а также удобно редактировать файл `~/.ssh/config`.


---

## 📦 Возможности

- Генерация новых SSH-ключей (`ed25519`, `rsa`)
- Просмотр и удаление ключей
- Отображение публичного ключа и копирование в буфер
- Редактирование `~/.ssh/config` (добавление, изменение, удаление хостов)
- Поддержка RPM-сборки

---

## 🧱 Установка

### Через RPM (Fedora, RHEL-based)

```bash
sudo dnf install ./ssh-key-manager-1.0-*.noarch.rpm
```

Из исходников

```bash
git clone https://github.com/threenet3/ssh-key-manager.git
cd ssh-key-manager
pip install .
```

## 🚀 Запуск

```bash
ssh-key-manager
```

## 🛠️ Зависимости

- Python 3.8+
- Tkinter (python3-tkinter)
- Pillow (pillow)
- pyperclip
- openssh-clients

## 🗂️ Структура проекта

```
ssh_key_manager/
├── core/           # Логика работы с ключами и ssh-конфигурацией
├── gui/            # Интерфейс на Tkinter
├── utils/          # Валидаторы и работа с файлами
├── assets/         # Иконка GUI
├── main.py         # Точка входа (main())
├── pyproject.toml  # Метаинформация и зависимости
├── setup.spec      # RPM-спецификация
```

## 📜 Лицензия
Проект распространяется под лицензией [MIT]().
