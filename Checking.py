import sqlite3


con = sqlite3.connect('Data/Accounting.sqlite')
cur = con.cursor()

def check_password(password):
    lenght_error = 'Длина пароля должна быть не менее 8 знаков'
    letter_case_error = 'В пароле должны быть буквы различного регистра'
    digit_error = 'В пароле должна быть хотя бы одна цифра'
    if len(password) < 8:
        return lenght_error
    if password.lower() == password or password.upper() == password:
        return letter_case_error
    if not any([i in password for i in list('0123456789')]):
        return digit_error
    # Если ошибки нет, сообщаем о ее отсутствии
    return False

def check_name(name):
    return len(cur.execute(f"""SELECT * FROM Companies
                    WHERE Name = '{name}'""").fetchall())

def check_email(email):
    return email.count('@') == 1 and email[email.find('@'):].count('.') == 1
