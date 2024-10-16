import os

bot_dir = os.path.dirname(os.path.abspath(__file__))
selected_dir = os.path.abspath(os.path.join(bot_dir, os.pardir, os.pardir))
file_path = os.path.join(selected_dir, 'token.txt')
if os.path.exists(file_path):
    with open(file_path, 'r') as file:
        token = file.read().strip()
    print(f'BOT_TOKEN: {token}')

else:
    print(f'Ошибка: файл по пути {file_path} не найден.')
    
BOT_TOKEN = f"{token}"