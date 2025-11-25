import unittest
from unittest.mock import MagicMock, patch, call
import sys
import os

# Додаємо кореневу директорію в шлях, щоб імпортувати модуль
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from koch_snowflake_drawer import koch_curve, draw_koch_snowflake, main

class TestKochCurve(unittest.TestCase):
    def test_koch_curve_order_0(self):
        """Перевіряє базовий випадок: просто лінія вперед."""
        mock_turtle = MagicMock()
        koch_curve(mock_turtle, order=0, size=100)
        
        # Має бути лише один рух вперед
        mock_turtle.forward.assert_called_once_with(100)
        # Ніяких поворотів
        mock_turtle.left.assert_not_called()
        mock_turtle.right.assert_not_called()

    def test_koch_curve_order_1(self):
        """Перевіряє перший рівень рекурсії."""
        mock_turtle = MagicMock()
        koch_curve(mock_turtle, order=1, size=90)
        
        # При order 1 лінія ділиться на 4 частини (рекурсивні виклики order 0)
        # size стає 30.0
        # forward викликається 4 рази
        self.assertEqual(mock_turtle.forward.call_count, 4)
        mock_turtle.forward.assert_has_calls([call(30.0)] * 4)
        
        # Перевіряємо структуру поворотів: Left 60 -> Right 120 -> Left 60
        expected_calls = [
            call.left(60),
            call.right(120),
            call.left(60)
        ]
        # Фільтруємо тільки виклики left/right для перевірки послідовності
        actual_calls = [c for c in mock_turtle.mock_calls if 'left' in c[0] or 'right' in c[0]]
        self.assertEqual(actual_calls, expected_calls)

class TestDrawKochSnowflake(unittest.TestCase):
    @patch('turtle.Screen')
    @patch('turtle.Turtle')
    def test_draw_snowflake_setup(self, MockTurtle, MockScreen):
        """Перевіряє налаштування вікна та черепашки."""
        mock_screen_instance = MockScreen.return_value
        mock_turtle_instance = MockTurtle.return_value
        
        draw_koch_snowflake(order=0, size=300)
        
        # Перевірка налаштувань екрану
        mock_screen_instance.bgcolor.assert_called_with("white")
        mock_screen_instance.tracer.assert_called_with(0) # Оптимізація має бути увімкнена
        
        # Перевірка позиціонування
        mock_turtle_instance.penup.assert_called()
        mock_turtle_instance.goto.assert_called_with(-150.0, 100.0)
        mock_turtle_instance.pendown.assert_called()
        
        # Перевірка циклу (сніжинка - це 3 криві)
        # Оскільки order=0, то forward викликається 3 рази (по 1 на сторону)
        self.assertEqual(mock_turtle_instance.forward.call_count, 3)
        
        # Перевірка оновлення та запуску
        mock_screen_instance.update.assert_called()
        mock_screen_instance.mainloop.assert_called()

class TestMainInput(unittest.TestCase):
    @patch('builtins.print')
    @patch('koch_snowflake_drawer.draw_koch_snowflake')
    @patch('builtins.input')
    def test_main_valid_input(self, mock_input, mock_draw, mock_print):
        """Тест звичайного введення (наприклад, '2')."""
        mock_input.return_value = '2'
        main()
        mock_draw.assert_called_once_with(2)

    @patch('builtins.print')
    @patch('koch_snowflake_drawer.draw_koch_snowflake')
    @patch('builtins.input')
    def test_main_empty_input(self, mock_input, mock_draw, mock_print):
        """Тест порожнього введення (має використати дефолт 0)."""
        mock_input.return_value = '   '
        main()
        mock_print.assert_any_call("Ви нічого не ввели. Використовую рівень 0.")
        mock_draw.assert_called_once_with(0)

    @patch('builtins.print')
    @patch('koch_snowflake_drawer.draw_koch_snowflake')
    @patch('builtins.input')
    def test_main_negative_input(self, mock_input, mock_draw, mock_print):
        """Тест від'ємного числа."""
        mock_input.return_value = '-5'
        main()
        mock_print.assert_any_call("Рівень не може бути від'ємним.")
        mock_draw.assert_not_called()

    @patch('builtins.print')
    @patch('koch_snowflake_drawer.draw_koch_snowflake')
    @patch('builtins.input')
    def test_main_bad_input_string(self, mock_input, mock_draw, mock_print):
        """Тест введення тексту замість числа."""
        mock_input.return_value = 'abc'
        main()
        mock_print.assert_any_call("Помилка: потрібно ввести ціле число.")
        mock_draw.assert_not_called()

    @patch('builtins.print')
    @patch('koch_snowflake_drawer.draw_koch_snowflake')
    @patch('builtins.input')
    def test_main_keyboard_interrupt(self, mock_input, mock_draw, mock_print):
        """Тест натискання Ctrl+C."""
        mock_input.side_effect = KeyboardInterrupt
        main()
        mock_print.assert_any_call("\nПрограма зупинена користувачем.")
        mock_draw.assert_not_called()

if __name__ == '__main__':
    unittest.main()
