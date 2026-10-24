
import socket
import threading

# Налаштування адреси та порту сервера
HOST = '0.0.0.0'
PORT = 8080

# Список підключених клієнтів
clients = []


def broadcast(data, exclude_socket=None):
    # Надсилаємо повідомлення всім клієнтам, крім відправника
    for client in clients:
        if client != exclude_socket:
            try:
                client.sendall(data)
            except:
                print("ERROR")  # Помилка надсилання повідомлення


def handle_client(client_socket):
    # Отримуємо повідомлення від клієнта
    while True:
        try:
            data = client_socket.recv(4096)

            if not data:
                break  # Клієнт відключився

            # Пересилаємо повідомлення іншим клієнтам
            broadcast(data, exclude_socket=client_socket)

        except:
            break  # Завершуємо роботу при помилці

    # Видаляємо клієнта зі списку після відключення
    if client_socket in clients:
        clients.remove(client_socket)

    # Закриваємо з'єднання з клієнтом
    client_socket.close()


def main():
    # Створюємо TCP-сокет сервера
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Дозволяємо повторно використовувати адресу після завершення роботи
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Прив'язуємо сервер до адреси та порту
    server_socket.bind((HOST, PORT))

    # Починаємо очікувати підключення клієнтів
    server_socket.listen(5)
    print(f"Сервер запущено на {HOST}:{PORT}")

    while True:
        # Приймаємо нове підключення
        client_socket, addr = server_socket.accept()
        print(f"Підключився клієнт: {addr}")

        # Додаємо клієнта до списку
        clients.append(client_socket)

        # Запускаємо окремий потік для кожного клієнта
        t = threading.Thread(
            target=handle_client,
            args=(client_socket,)
        )
        t.start()


# Запускаємо сервер при виконанні цього файлу
if __name__ == "__main__":
    main()
