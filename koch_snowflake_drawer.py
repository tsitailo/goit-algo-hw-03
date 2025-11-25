import turtle


def koch_curve(t, order, size):
    if order == 0:
        t.forward(size)
    else:
        size /= 3.0
        koch_curve(t, order - 1, size)
        t.left(60)
        koch_curve(t, order - 1, size)
        t.right(120)
        koch_curve(t, order - 1, size)
        t.left(60)
        koch_curve(t, order - 1, size)


def draw_koch_snowflake(order, size=300):
    window = turtle.Screen()
    window.bgcolor("white")
    window.title(f"Сніжинка Коха (Рівень {order})")

    # ВАЖЛИВО: Вимикаємо анімацію для миттєвого малювання
    # Це вирішує проблему "зависання" при малюванні
    window.tracer(0)

    t = turtle.Turtle()
    t.hideturtle()  # Ховаємо саму черепашку, щоб не заважала
    t.penup()
    t.goto(-size / 2, size / 3)
    t.pendown()

    print("Починаю малювання...")

    for _ in range(3):
        koch_curve(t, order, size)
        t.right(120)

    # ВАЖЛИВО: Примусово оновлюємо екран, коли все готово
    window.update()
    print("Малювання завершено. Клікніть по вікну, щоб закрити.")

    window.mainloop()


def main():
    try:
        print("--- ГЕНЕРАТОР СНІЖИНКИ КОХА ---")
        user_input = input("Введіть рівень рекурсії (0-5): ")

        # Перевірка на порожній ввід
        if not user_input.strip():
            print("Ви нічого не ввели. Використовую рівень 0.")
            order = 0
        else:
            order = int(user_input)

        if order < 0:
            print("Рівень не може бути від'ємним.")
        else:
            # Запускаємо малювання
            draw_koch_snowflake(order)

    except ValueError:
        print("Помилка: потрібно ввести ціле число.")
    except KeyboardInterrupt:
        print("\nПрограма зупинена користувачем.")


if __name__ == "__main__":
    main()