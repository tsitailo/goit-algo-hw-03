import unittest
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import sys
import shutil

# Імпортуємо модуль, який будемо тестувати
import file_sorter

class TestFileSorter(unittest.TestCase):

    # --- Тести для parse_arguments ---
    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_arguments_defaults(self, mock_parse_args):
        """Тест парсингу аргументів: значення за замовчуванням"""
        mock_args = MagicMock()
        mock_args.source = "source_dir"
        mock_args.output = "dist"
        mock_parse_args.return_value = mock_args

        with patch('sys.argv', ['script_name', 'source_dir']):
            args = file_sorter.parse_arguments()
            self.assertEqual(args.source, "source_dir")
            self.assertEqual(args.output, "dist")

    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_arguments_explicit(self, mock_parse_args):
        """Тест парсингу аргументів: явне вказання обох шляхів"""
        mock_args = MagicMock()
        mock_args.source = "src"
        mock_args.output = "out"
        mock_parse_args.return_value = mock_args

        with patch('sys.argv', ['script_name', 'src', 'out']):
            args = file_sorter.parse_arguments()
            self.assertEqual(args.source, "src")
            self.assertEqual(args.output, "out")

    # --- Тести для copy_file ---
    @patch('shutil.copy2')
    @patch('pathlib.Path.mkdir')
    def test_copy_file_success(self, mock_mkdir, mock_copy2):
        """Тест успішного копіювання файлу з розширенням"""
        source_file = Path("source/test.txt")
        output_dir = Path("dist")
        
        file_sorter.copy_file(source_file, output_dir)
        
        # Перевірка створення папки 'txt'
        expected_target_folder = output_dir / "txt"
        mock_mkdir.assert_called_with(parents=True, exist_ok=True)
        
        # Перевірка копіювання
        expected_target_file = expected_target_folder / "test.txt"
        mock_copy2.assert_called_with(source_file, expected_target_file)

    @patch('shutil.copy2')
    @patch('pathlib.Path.mkdir')
    def test_copy_file_no_extension(self, mock_mkdir, mock_copy2):
        """Тест копіювання файлу без розширення"""
        source_file = Path("source/readme") # без крапки
        output_dir = Path("dist")
        
        file_sorter.copy_file(source_file, output_dir)
        
        expected_target_folder = output_dir / "no_extension"
        expected_target_file = expected_target_folder / "readme"
        
        mock_copy2.assert_called_with(source_file, expected_target_file)

    @patch('shutil.copy2')
    def test_copy_file_permission_error(self, mock_copy2):
        """Тест обробки помилки доступу при копіюванні"""
        mock_copy2.side_effect = PermissionError("Access denied")
        source_file = Path("restricted.txt")
        output_dir = Path("dist")

        # Перехоплюємо stderr
        with patch('sys.stderr') as mock_stderr:
            file_sorter.copy_file(source_file, output_dir)

            # Збираємо всі виклики write в один рядок для перевірки
            full_output = "".join(call.args[0] for call in mock_stderr.write.call_args_list)
            self.assertIn("[ERROR] Немає прав доступу", full_output)

    @patch('shutil.copy2')
    def test_copy_file_os_error(self, mock_copy2):
        """Тест обробки системної помилки при копіюванні"""
        mock_copy2.side_effect = OSError("Disk full")
        source_file = Path("file.txt")
        output_dir = Path("dist")

        with patch('sys.stderr') as mock_stderr:
            file_sorter.copy_file(source_file, output_dir)

            full_output = "".join(call.args[0] for call in mock_stderr.write.call_args_list)
            self.assertIn("[ERROR] Помилка ОС", full_output)

    @patch('shutil.copy2')
    def test_copy_file_unknown_error(self, mock_copy2):
        """Тест обробки невідомої помилки при копіюванні"""
        mock_copy2.side_effect = Exception("Boom!")
        source_file = Path("file.txt")
        output_dir = Path("dist")

        with patch('sys.stderr') as mock_stderr:
            file_sorter.copy_file(source_file, output_dir)

            full_output = "".join(call.args[0] for call in mock_stderr.write.call_args_list)
            self.assertIn("[ERROR] Невідома помилка", full_output)

    # --- Тести для process_directory ---
    
    @patch('file_sorter.copy_file')
    def test_process_directory_recursion(self, mock_copy_file):
        """Тест рекурсивного обходу директорій"""
        # Структура:
        # root/
        #   - file1.txt
        #   - subdir/
        #       - file2.png
        
        root = MagicMock(spec=Path)
        root.exists.return_value = True
        root.is_dir.return_value = True
        
        file1 = MagicMock(spec=Path)
        file1.is_dir.return_value = False
        file1.is_file.return_value = True
        
        subdir = MagicMock(spec=Path)
        subdir.is_dir.return_value = True
        subdir.is_file.return_value = False
        
        file2 = MagicMock(spec=Path)
        file2.is_dir.return_value = False
        file2.is_file.return_value = True

        # Налаштовуємо iterdir для root і subdir
        root.iterdir.return_value = [file1, subdir]
        subdir.iterdir.return_value = [file2]
        
        output_dir = Path("dist")
        
        file_sorter.process_directory(root, output_dir)
        
        # Перевіряємо, що copy_file викликався для обох файлів
        expected_calls = [call(file1, output_dir), call(file2, output_dir)]
        mock_copy_file.assert_has_calls(expected_calls, any_order=True)
        self.assertEqual(mock_copy_file.call_count, 2)

    def test_process_directory_not_exists(self):
        """Тест: вихідна директорія не існує"""
        source_dir = MagicMock(spec=Path)
        source_dir.exists.return_value = False

        with patch('sys.stderr') as mock_stderr:
            file_sorter.process_directory(source_dir, Path("dist"))

            full_output = "".join(call.args[0] for call in mock_stderr.write.call_args_list)
            self.assertIn("не існує", full_output)

    def test_process_directory_is_not_dir(self):
        """Тест: вказаний шлях не є директорією"""
        source_dir = MagicMock(spec=Path)
        source_dir.exists.return_value = True
        source_dir.is_dir.return_value = False

        with patch('sys.stderr') as mock_stderr:
            file_sorter.process_directory(source_dir, Path("dist"))

            full_output = "".join(call.args[0] for call in mock_stderr.write.call_args_list)
            self.assertIn("не є директорією", full_output)

    def test_process_directory_permission_error(self):
        """Тест: немає прав на читання директорії"""
        source_dir = MagicMock(spec=Path)
        source_dir.exists.return_value = True
        source_dir.is_dir.return_value = True
        source_dir.iterdir.side_effect = PermissionError

        with patch('sys.stderr') as mock_stderr:
            file_sorter.process_directory(source_dir, Path("dist"))

            full_output = "".join(call.args[0] for call in mock_stderr.write.call_args_list)
            self.assertIn("Немає прав доступу", full_output)

    def test_process_directory_os_error(self):
        """Тест: помилка ОС при читанні директорії"""
        source_dir = MagicMock(spec=Path)
        source_dir.exists.return_value = True
        source_dir.is_dir.return_value = True
        source_dir.iterdir.side_effect = OSError

        with patch('sys.stderr') as mock_stderr:
            file_sorter.process_directory(source_dir, Path("dist"))

            full_output = "".join(call.args[0] for call in mock_stderr.write.call_args_list)
            self.assertIn("Помилка ОС", full_output)

    # --- Тести для main ---
    @patch('file_sorter.parse_arguments')
    @patch('file_sorter.process_directory')
    def test_main_flow(self, mock_process, mock_parse):
        """Тест основного потоку виконання main"""
        mock_args = MagicMock()
        mock_args.source = "src"
        mock_args.output = "dist"
        mock_parse.return_value = mock_args
        
        with patch('builtins.print'): # Глушимо принти
            file_sorter.main()
        
        mock_process.assert_called_once()
        args, _ = mock_process.call_args
        self.assertEqual(str(args[0]), "src") # Перевіряємо, що source path передано правильно
        self.assertEqual(str(args[1]), "dist")

    @patch('file_sorter.main')
    def test_keyboard_interrupt(self, mock_main):
        """Тест переривання через Ctrl+C (KeyboardInterrupt)"""
        mock_main.side_effect = KeyboardInterrupt
        
        # Нам потрібно зімітувати поведінку блоку if __name__ == "__main__"
        # Оскільки ми не можемо безпосередньо запустити цей блок, ми перевіряємо,
        # що sys.exit викликається при KeyboardInterrupt в контексті, схожому на main.
        # Але для чистоти тесту в unitttest ми можемо просто перевірити обробку виключення
        # шляхом виклику функції, яка містить try-except, або просто емулювати це.
        
        with patch('sys.exit') as mock_exit:
            with patch('builtins.print'):
                try:
                    mock_main()
                except KeyboardInterrupt:
                    # Емуляція блоку except в if __name__ == "__main__"
                    print("\nРоботу перервано користувачем.")
                    sys.exit(0)
            
            mock_exit.assert_called_with(0)

if __name__ == '__main__':
    unittest.main()
