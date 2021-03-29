# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# import json
#
#
# scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/spreadsheets',
#          'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']
#
#
# with open('TRRP1-20c5117d16b6.json', 'r') as file:
#     t = json.loads(file.read())
#
# creds = ServiceAccountCredentials.from_json_keyfile_dict(t, scope)
#
# client = gspread.authorize(creds)
#
# sheet = client.open('ТРРП1').sheet1
#
# data = sheet.cell(1, 2).value
#
# print(data)
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


# TRRP1-20c5117d16b6.json
# {
#   "type": "service_account",
#   "project_id": "trrp1-309012",
#   "private_key_id": "20c5117d16b6b3f90afd53931b3dd152c2dc459d",
#   "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDHUj8H2fjTVVKz\n+L/NlRKf85KKNe3Su3VDs6h5qmPm6IempxPvw7DsW/HJankJmvOVIUkOLcxRSER7\nVgfRYV3PmKK1YvMVb+hhnuBypXlp5EF6UTNnhrgaNWgjaGHXyR9AAn6B+4Kxv88e\ntfnJI0Om8YUecbS3F7imVIFtBZrKl4edjpggPczbeQJBCwfBQnNwDqaelhy8EtOi\nZQtS66Fzxc3j1Z71BrLWNRBC/oTW0t2U87Ev7p0+md8Y7i58b6AGmXdN8BO2TRoO\n49k0nZ3jBtrO+p+GQ588lfTrZ1n8jk+ZPekC0DiidB5Ckelmb5rABbq4JA+na0Qc\neaN8qLaFAgMBAAECggEAXp454pnEB1pVEK8QKeDOvxRqp2ZzV5p6T6Gs49iRZQ9U\nObXNfn94cLMy44jCHV+rqsrquare92TlcWEFBA2C8WXFM3Ld7vq5JwI7DOFlcfGT\nbaO3Ubk/kt1waoKGE9/bEFE+yahhwcxKX4tGIIe3eTvkk++pOFMv6fFqoRzMfse6\nES6I32buqnOldVWWHsSI+BF/AXaud5I0+vFObdDF5HJ+1WrMZIxxqB+VdSJ/bpx2\nkNX99ALd3GDuFYMeBATecIVkrEiTDwP7uEF5ss1mNdS2w4r2v81op+kikovCE5fx\n2JKMwpYOXo73dbMLWIgBTImZ8qqVoc8eMlZaPsC3fwKBgQDwIMk4NiZUlLqqmFCN\n51vmOzjDGQc055UWP2eV/kbCCUuorwxQjgTDvGn2rNkczxdPDTfTkGBBby+V+71e\nnQ4a8if+J9c5fJl4FVZFMADdWyDdK7lOuKzpciQlkzh56eJ3j7MxpUSFM/DaYwKa\nzX5jUebJaH+KOBx0AZhQyRjpZwKBgQDUfvecUnM4OpyfLvN25fRUIpnVuPMBLCaC\nvDMT6vs4Hq7lvijr7R/5s/LOmbJ6rgLyomgk6r9j/d47nYIEW8JaD5oeEl3dL99D\nfZPMq6m7mIiNf6CA0uL/wZmz9jzmcGeTICfALFO5rjNMU7Ir+oDaxSk+v9/EAcgH\nw7eHVN6xMwKBgBN7RXf3BLMWAfL3OonYvF74bQl/DVOgejr81+WWZJ03bdj4orIi\nY4aR0bL+oPqyXny+YMocS4Ljh2POsbVsXomXHeGDz/VNA5J3gLFKTLeovgjTlEwr\ntXOXHBGkWQ+jBwmWMf6UHvQDm8XMBJkUlO1v5p5uiPJozP4oZvge6JN/AoGAWB/r\numWrKPeNuqpzB60oHbhXyf2wsZzIv9Ei8bCyzLxU1ix9thIZ/6l0GeA914jQ6iUW\nQbEk/GftQRX6NKqFOGpeBPii+rb+xXOP1wKeGpGQl/YE70gGIgD9KFgHO54EJkzg\nj18Svd+ToKTZMEnsJE4946sZNqVyel3df/9fd2cCgYBkPZpt6ZmyOvPK/7cNT2SU\nTVEwKlyWfJSB+5Kun/vyE9ZPe+8MuVSjSRvZat8GAwb8Nnpt5UDPRXP6DSriSDP5\nPWpSN9ttndCkEvT/ia6rBvQclGzcitHLQ1XW4zLZKAN92rnvYP6zznVdG6EKIwE3\ng3WckSsf/sG9rhmfl1qxww==\n-----END PRIVATE KEY-----\n",
#   "client_email": "damir-328@trrp1-309012.iam.gserviceaccount.com",
#   "client_id": "109717739470725967932",
#   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#   "token_uri": "https://oauth2.googleapis.com/token",
#   "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#   "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/damir-328%40trrp1-309012.iam.gserviceaccount.com"
# }
#
