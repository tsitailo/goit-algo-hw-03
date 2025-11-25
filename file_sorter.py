import argparse
import shutil
from pathlib import Path
import sys

def parse_arguments():
    """
    Парсинг аргументів командного рядка.
    Повертає об'єкт з атрибутами source та output.
    """
    parser = argparse.ArgumentParser(description="Рекурсивне копіювання та сортування файлів за розширенням.")
    parser.add_argument("source", type=str, help="Шлях до вихідної директорії")
    parser.add_argument("output", nargs="?", default="dist", help="Шлях до директорії призначення (за замовчуванням: dist)")
    return parser.parse_args()

def copy_file(file_path: Path, output_dir: Path):
    """
    Копіює файл у відповідну піддиректорію в output_dir на основі його розширення.
    """
    try:
        # Отримуємо розширення файлу (без крапки). Якщо розширення немає, використовуємо 'no_extension'
        extension = file_path.suffix[1:].lower() if file_path.suffix else "no_extension"
        
        # Формуємо шлях до цільової папки
        target_folder = output_dir / extension
        
        # Створюємо папку, якщо вона не існує
        target_folder.mkdir(parents=True, exist_ok=True)
        
        # Формуємо повний шлях до цільового файлу
        target_file = target_folder / file_path.name
        
        # Копіюємо файл
        shutil.copy2(file_path, target_file)
        print(f"[OK] Скопійовано: {file_path} -> {target_file}")
        
    except PermissionError:
        print(f"[ERROR] Немає прав доступу для копіювання файлу: {file_path}", file=sys.stderr)
    except OSError as e:
        print(f"[ERROR] Помилка ОС при копіюванні {file_path}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"[ERROR] Невідома помилка з файлом {file_path}: {e}", file=sys.stderr)

def process_directory(source_dir: Path, output_dir: Path):
    """
    Рекурсивно читає директорію та обробляє файли.
    """
    try:
        # Перевіряємо, чи існує вихідна директорія
        if not source_dir.exists():
            print(f"[ERROR] Вихідна директорія не існує: {source_dir}", file=sys.stderr)
            return
        
        if not source_dir.is_dir():
             print(f"[ERROR] Шлях не є директорією: {source_dir}", file=sys.stderr)
             return

        # Перебираємо всі елементи в директорії
        for item in source_dir.iterdir():
            if item.is_dir():
                # Рекурсивний виклик для підпапок
                process_directory(item, output_dir)
            elif item.is_file():
                # Копіювання файлу
                copy_file(item, output_dir)
                
    except PermissionError:
        print(f"[ERROR] Немає прав доступу до директорії: {source_dir}", file=sys.stderr)
    except OSError as e:
        print(f"[ERROR] Помилка ОС при читанні директорії {source_dir}: {e}", file=sys.stderr)

def main():
    args = parse_arguments()
    
    source_path = Path(args.source)
    output_path = Path(args.output)
    
    print(f"Початок роботи.")
    print(f"Вихідна папка: {source_path.absolute()}")
    print(f"Папка призначення: {output_path.absolute()}")
    print("-" * 40)

    process_directory(source_path, output_path)
    
    print("-" * 40)
    print("Роботу завершено.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nРоботу перервано користувачем.")
        sys.exit(0)
