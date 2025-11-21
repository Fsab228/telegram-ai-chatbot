import pathlib

base = pathlib.Path(__file__).parent
files_to_delete = [".env", "bot_database.db", "bot.log"]

print("🧹 Очистка проекта...\n")

for file_name in files_to_delete:
    file_path = base / file_name
    if file_path.exists():
        try:
            file_path.unlink()
            print(f"✅ Удален: {file_name}")
        except Exception as e:
            print(f"❌ Ошибка при удалении {file_name}: {e}")
    else:
        print(f"⏭️  Не найден: {file_name}")

import shutil
for cache_dir in base.rglob("__pycache__"):
    if cache_dir.is_dir():
        try:
            shutil.rmtree(cache_dir)
            print(f"✅ Удалена папка: {cache_dir.relative_to(base)}")
        except Exception as e:
            print(f"❌ Ошибка при удалении {cache_dir}: {e}")

print("\n✨ Очистка завершена!")
print("📝 Проект готов к загрузке на GitHub.")

