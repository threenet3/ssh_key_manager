# SSH Key Manager

**Графическая утилита для управления SSH-ключами** на Python с использованием Tkinter. Позволяет создавать, удалять, просматривать и назначать SSH-ключи, а также удобно редактировать файл `~/.ssh/config`.

- [Изображение №1]("screenshots/1.png")
- [Изображение №2]("screenshots/2.png")
- [Изображение №3]("screenshots/3.png")
- [Изображение №4]("screenshots/4.png")
- [Изображение №5]("screenshots/5.png")

---

## 📦 Возможности

- Генерация новых SSH-ключей (`ed25519`, `rsa`, `ECDSA`)
- Просмотр и удаление ключей
- Отображение публичного ключа и копирование в буфер
- Редактирование `~/.ssh/config` (добавление, изменение, удаление хостов)
- Поддержка RPM-сборки

---

## 🧱 Установка

**RPM**

```bash
sudo dnf install ./ssh-key-manager-1.0-*.noarch.rpm
```

## 🚀 Запуск

```bash
ssh-key-manager
```

## 🛠️ Зависимости

- Python 3.8+
- Tkinter
- Pillow (PillowTk)
- pyperclip
- openssh-clients

## 🗂️ Структура проекта

```
ssh_key_manager/
├── core/...            # Логика работы с ключами и ssh-конфигурацией
├── gui/...             # Интерфейс на Tkinter
├── utils/...           # Валидаторы и работа с файлами
├── assets/...          # Иконка GUI
├── main.py             # Точка входа (main())
├── pyproject.toml      # Метаинформация и зависимости
├── setup.spec          # RPM-спецификация
```

## 📜 Лицензия
Проект распространяется под лицензией [MIT](https://github.com/threenet3/ssh_key_manager/tree/main?tab=License-1-ov-file).
