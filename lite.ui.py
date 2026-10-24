
import threading
from socket import *
from customtkinter import *


class MainWindow(CTk):
    def __init__(self):
        super().__init__()

        # Налаштування головного вікна
        self.geometry('400x300')
        self.label = None

        # Створення бічного меню
        self.menu_frame = CTkFrame(self, width=30, height=300)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.place(x=0, y=0)

        # Змінні для анімації меню
        self.is_show = False
        self.speed_animate_menu = -5

        # Кнопка відкриття та закриття меню
        self.btn = CTkButton(
            self, text='▶️',
            command=self.toggle_show_menu, width=30
        )
        self.btn.place(x=0, y=0)

        # Поле для відображення повідомлень
        self.chat_field = CTkTextbox(
            self, font=('Arial', 14, 'bold'), state='disable'
        )
        self.chat_field.place(x=0, y=0)

        # Поле для введення повідомлення
        self.message_entry = CTkEntry(
            self, placeholder_text='Введіть повідомлення:', height=40
        )
        self.message_entry.place(x=0, y=0)

        # Кнопка надсилання повідомлення
        self.send_button = CTkButton(
            self, text='>', width=50, height=40,
            command=self.send_message
        )
        self.send_button.place(x=0, y=0)

        self.username = 'Artem'  # Ім'я користувача

        # Підключення до сервера
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('localhost', 8080))

            # Повідомлення про приєднання до чату
            hello = (
                f"TEXT@{self.username}@[SYSTEM] "
                f"{self.username} приєднався(лась) до чату!\n"
            )
            self.sock.send(hello.encode('utf-8'))

            # Запуск потоку для отримання повідомлень
            threading.Thread(
                target=self.recv_message, daemon=True
            ).start()

        except Exception as e:
            # Виведення помилки підключення
            self.add_message(f"Не вдалося підключитися до сервера: {e}")

        # Налаштування розмірів елементів вікна
        self.adaptive_ui()

    def toggle_show_menu(self):
        # Відкриваємо або закриваємо бічне меню
        if self.is_show_menu:
            self.is_show_menu = False
            self.speed_animate_menu *= -1
            self.btn.configure(text='▶️')
            self.show_menu()
        else:
            self.is_show_menu = True
            self.speed_animate_menu *= -1
            self.btn.configure(text='◀️')
            self.show_menu()

            # Додаємо поле для введення імені
            self.label = CTkLabel(self.menu_frame, text='Імʼя')
            self.label.pack(pady=30)

            self.entry = CTkEntry(self.menu_frame)
            self.entry.pack()

    def show_menu(self):
        # Змінюємо ширину меню для створення анімації
        self.menu_frame.configure(
            width=self.menu_frame.winfo_width()
            + self.speed_animate_menu
        )

        # Продовжуємо анімацію відкриття меню
        if not self.menu_frame.winfo_width() >= 200 and self.is_show_menu:
            self.after(10, self.show_menu)

        # Продовжуємо анімацію закриття меню
        elif self.menu_frame.winfo_width() >= 40 and not self.is_show_menu:
            self.after(10, self.show_menu)

            # Видаляємо поля меню після закриття
            if self.label and self.entry:
                self.label.destroy()
                self.entry.destroy()

    def adaptive_ui(self):
        # Підлаштовуємо меню під висоту вікна
        self.menu_frame.configure(height=self.winfo_height())

        # Розміщуємо поле чату поруч із меню
        self.chat_field.place(x=self.menu_frame.winfo_width())

        # Змінюємо розмір поля чату відповідно до вікна
        self.chat_field.configure(
            width=self.winfo_width() - self.menu_frame.winfo_width(),
            height=self.winfo_height() - 40
        )

        # Розміщуємо кнопку надсилання внизу праворуч
        self.send_button.place(
            x=self.winfo_width() - 50,
            y=self.winfo_height() - 40
        )

        # Розміщуємо поле введення біля кнопки
        self.message_entry.place(
            x=self.menu_frame.winfo_width(),
            y=self.send_button.winfo_y()
        )

        # Налаштовуємо ширину поля введення
        self.message_entry.configure(
            width=self.winfo_width()
            - self.menu_frame.winfo_width()
            - self.send_button.winfo_width()
        )

        # Повторюємо налаштування для адаптації вікна
        self.after(50, self.adaptive_ui)

    def add_message(self, text):
        # Тимчасово дозволяємо редагування поля чату
        self.chat_field.configure(state='normal')

        # Додаємо повідомлення до чату
        self.chat_field.insert(END, 'Я: ' + text + '\n')

        # Забороняємо редагування поля чату
        self.chat_field.configure(state='disable')

    def send_message(self):
        # Отримуємо текст із поля введення
        message = self.message_entry.get()

        if message:
            # Відображаємо повідомлення у вікні чату
            self.add_message(f"{self.username}: {message}")

            # Формуємо дані для надсилання на сервер
            data = f"TEXT@{self.username}@{message}\n"

            try:
                self.sock.sendall(data.encode())
            except:
                pass  # Ігноруємо помилку надсилання

        # Очищаємо поле введення
        self.message_entry.delete(0, END)

    def recv_message(self):
        # Буфер для накопичення отриманих даних
        buffer = ""

        while True:
            try:
                # Отримуємо дані від сервера
                chunk = self.sock.recv(4096)

                if not chunk:
                    break

                buffer += chunk.decode()

                # Обробляємо кожне завершене повідомлення
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle_line(line.strip())

            except:
                break  # Завершуємо отримання в разі помилки

        # Закриваємо з'єднання із сервером
        self.sock.close()

    def handle_line(self, line):
        # Ігноруємо порожні повідомлення
        if not line:
            return

        # Розділяємо повідомлення на частини
        parts = line.split("@", 3)
        msg_type = parts[0]

        # Обробка текстових повідомлень
        if msg_type == "TEXT":
            if len(parts) >= 3:
                author = parts[1]
                message = parts[2]

                # Відображаємо ім'я автора та текст
                self.add_message(f"{author}: {message}")

        # Обробка повідомлень про зображення
        elif msg_type == "IMAGE":
            if len(parts) >= 4:
                author = parts[1]
                filename = parts[2]

                # Повідомляємо про надіслане зображення
                self.add_message(
                    f"{author} надіслав(ла) зображення: {filename}"
                )

        else:
            # Відображаємо інші типи повідомлень
            self.add_message(line)


# Створення та запуск вікна чату
win = MainWindow()
win.mainloop()
