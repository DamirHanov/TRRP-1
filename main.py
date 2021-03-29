import os
import hashlib
from Crypto.Cipher import AES
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

ENCRYPTED_FILENAME = 'credentials'


def load_credentials_file():
    if os.path.isfile(ENCRYPTED_FILENAME):
        with open(ENCRYPTED_FILENAME, 'rb') as credentials:
            encrypted = credentials.read()
        password = input('Введите пароль для расшифровки: ')
        password = hashlib.sha256(password.encode())
        try:
            cypher = AES.new(password.digest(), AES.MODE_ECB)
            return cypher.decrypt(encrypted).decode()
        except UnicodeDecodeError:
            print('Неверный пароль!')
            exit(1)
    else:
        print('Файл с сохранённой информацией для фхода не найден!')
        while True:
            path = input('Введите путь до файла с информацией для авторизации: ')
            if not os.path.isfile(path):
                print('Указан неверный файл с информацией для авторизации. Попробуйте ввести путь заново.')
            else:
                break
        with open(path) as credentials:
            return credentials.read()


def get_cell_coordinates():
    coordinates = input('Введите координаты ячейки [ строка, столбец ] через пробел: ').split()
    if len(coordinates) != 2 or not all([x.isdigit() for x in coordinates]) or not all(
            [int(x) >= 0 for x in coordinates]):
        print('Введены некорректные координаты')
    x, y = map(int, coordinates)
    return x, y


def get_agreement_and_number():
    action = input('Вы хотите продолжить? [Y/N] ')
    if action.upper() != 'Y':
        return None
    row_number = input('Введите номер строки: ')
    if not row_number.isdigit():
        print('Необходимо ввести число!')
        return None
    row_number = int(row_number)
    if row_number <= 0:
        print('Номер строки должен быть >= 1!')
        return None
    return row_number


def main():
    credentials = load_credentials_file()
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']
    try:
        credentials = json.loads(credentials)
    except json.decoder.JSONDecodeError:
        print(f'Не могу открыть файл!\nПопробуйте удалить файл {ENCRYPTED_FILENAME} и запустить программу заново')
        exit(1)
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
    except ValueError or NotImplementedError:
        print('Проверьте содержимое файла с данными для аутентификации!')
        exit(1)
    client = gspread.authorize(creds)
    sheet_name = credentials.get('sheet_name') or input('Введите название таблицы: ')
    try:
        sheet = client.open(sheet_name).sheet1
        credentials['sheet_name'] = sheet_name
    except gspread.exceptions.SpreadsheetNotFound:
        print('Не могу открыть таблицу!\nСкорее всего, не предоставлен доступ!')
        exit(1)
    while True:
        choice = input('Выберете действие:\n1. Создать новую строку\n2. Получить данные из ячейки\n3. Изменить данные '
                       'в ячейке\n4. Удалить строку\n5. Сохранить файл авторизации\n6. Удалить файл авторизации\n'
                       '7. Выйти\n')
        if choice == '1':
            print('Данные в таблице, ниже указанной строки будут смещены на 1 строчку вниз!')
            row_number = get_agreement_and_number()
            if not row_number:
                continue
            row_data = input('Введите содержимое столбцов, раздёляя их символом "|": ').split('|')
            sheet.insert_row(row_data, index=row_number)
        elif choice == '2':
            x, y = get_cell_coordinates()
            print(sheet.cell(x, y).value)
        elif choice == '3':
            x, y = get_cell_coordinates()
            new_data = input('Введите новые данные в ячейке: ')
            sheet.update_cell(x, y, new_data)
        elif choice == '4':
            print('Данные в таблице, ниже указанной строки будут смещены на 1 строчку вверх!')
            row_number = get_agreement_and_number()
            if not row_number:
                continue
            sheet.delete_row(row_number)
        elif choice == '5':
            if os.path.isfile(ENCRYPTED_FILENAME):
                action = input('Файл авторизации сохранён! Вы хотите сменить пароль [Y/N]: ')
                if action.upper() != 'Y':
                    continue
            password1 = input('Введите пароль для шифрования файла.\n')
            password2 = input('Введите пароль ещё раз.\n')
            if password1 == password2:
                password = hashlib.sha256(password1.encode()).digest()
                cypher = AES.new(password, AES.MODE_ECB)
                credentials = json.dumps(credentials)
                with open(ENCRYPTED_FILENAME, 'wb') as creds_file:
                    while len(credentials) % cypher.block_size != 0:
                        credentials += ' '

                    creds_file.write(cypher.encrypt(credentials.encode()))
        elif choice == '6':
            if os.path.isfile(ENCRYPTED_FILENAME):
                os.remove(ENCRYPTED_FILENAME)
        elif choice == '7':
            break
        else:
            print('Вы выбрали непаравильное действие!')


if __name__ == '__main__':
    main()
