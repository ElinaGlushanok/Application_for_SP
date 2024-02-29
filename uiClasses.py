import sqlite3
import datetime as dt

from Checking import check_password, check_name, check_email
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox

con = sqlite3.connect('Data/Accounting.sqlite')
cur = con.cursor()

# Класс окна регистрации
class Registrate(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI/Register.ui', self)
        self.setWindowTitle("Регистрация")
        self.RegistrateButton.clicked.connect(self.new_account)
        self.exitButton.setStyleSheet("background-color : blue")
        self.exitButton.clicked.connect(self.exit)

    # Возвращение в окно входа
    def exit(self):
        self.back = Enter()
        self.back.show()
        self.close()

    # Создание аккаунта
    def new_account(self):
        self.Password1Error.setText("")
        self.Password2Error.setText("")
        self.EmailError.setText("")
        company_is_registered = check_name(self.Name.text())
        # Проверка введенных данных на корректность и уведомление об ошибках
        if company_is_registered:
            self.Name.setText("Компания с таким названием уже существует")
            return

        password_is_uncorrect = check_password(self.Password1.text())
        if password_is_uncorrect:
            self.Password1Error.setText(password_is_uncorrect)
            return

        if self.Password1.text() != self.Password2.text():
            self.Password2Error.setText('Введенные пароли не совпадают')
            return

        email_is_currect = check_email(self.Email.text())
        if not email_is_currect:
            self.EmailError.setText('Почта введена некорректно')
            return

        #Создание новых таблиц в БД, соответствующих новому аккаунту
        cur.execute(f"""INSERT INTO Companies(Name, Password, Email) 
                        VALUES('{self.Name.text()}', '{self.Password1.text()}', '{self.Email.text()}')""")
        cur.execute(f'''CREATE TABLE IF NOT EXISTS {self.Name.text()}_products(
                        title TEXT, price INTEGER);''')
        cur.execute(f'''CREATE TABLE IF NOT EXISTS {self.Name.text()}_Data(
                            title TEXT, quantity INTEGER, cost INTEGER, date TEXT);''')
        con.commit()
        # Переход в личный кабинет
        self.go_to_account = PersonalAccount(self.Name.text())
        self.go_to_account.show()
        self.close()


# Класс окна входа в личный кабинет
class Enter(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI/Enter.ui', self)
        self.setWindowTitle("Вход")
        self.EnterButton.clicked.connect(self.enter)
        self.RegisterButton.clicked.connect(self.register)
        self.ForgotButton.clicked.connect(self.update)

    # Вход
    def enter(self):
        company_is_registered = check_name(self.Name.text())
        if not company_is_registered:
            self.Name.setText("Название введено неверно")
            return
        password = self.Password.text()
        cur_password = cur.execute(f'''SELECT Password FROM Companies 
                                    WHERE Name = "{self.Name.text()}"''').fetchall()[0]
        if password != cur_password[0]:
            self.Password.setText("Введен неверный пароль")
            return
        self.go_to_account = PersonalAccount(self.Name.text())
        self.go_to_account.show()
        self.close()

    # Регистрация
    def register(self):
        self.do_register = Registrate()
        self.do_register.show()
        self.close()

    # Обновление пароля
    def update(self):
        self.do_update = Update()
        self.do_update.show()
        self.close()


# Класс окна обновления пароля
class Update(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('UI/UpdatePassword.ui', self)
        self.setWindowTitle("Сброс пароля")
        self.MakeNewPassword.clicked.connect(self.set_new_password)
        self.exitButton.setStyleSheet("background-color : blue")
        self.exitButton.clicked.connect(self.exit)

    # Возвращение в окно входа
    def exit(self):
        self.back = Enter()
        self.back.show()
        self.close()

    # Установление нового пароля
    def set_new_password(self):
        self.NameError.setText("")
        self.EmailError.setText("")
        self.NewPasswError.setText("")
        self.NewPassw2Error.setText("")
        company_is_registered = check_name(self.Name.text())
        # Проверка корректности введенных данных
        if not company_is_registered:
            self.NameError.setText("Компании с таким названием не существует")
            return

        cur_email = cur.execute(f'''SELECT Email FROM Companies 
                                WHERE Name = "{self.Name.text()}"''').fetchall()[0]
        if self.Email.text() != cur_email[0]:
            self.EmailError.setText("Почта введена неверно")
            return

        password_is_uncorrect = check_password(self.NewPassword.text())
        if password_is_uncorrect:
            self.NewPasswError.setText(password_is_uncorrect)
            return

        if self.NewPassword.text() != self.NewPassword2.text():
            self.NewPassw2Error.setText('Введенные пароли не совпадают')
            return

        cur.execute(f'''UPDATE Companies SET Password = "{self.NewPassword.text()}"
                    WHERE Name = "{self.Name.text()}"''')
        con.commit()
        self.back = Enter()
        self.back.show()
        self.close()


# Класс окна личного кабинета
class PersonalAccount(QMainWindow):
    def __init__(self, company):
        super().__init__()
        uic.loadUi('UI/Work_table.ui', self)
        self.exitButton.setStyleSheet("background-color : blue")
        self.setWindowTitle('Личный кабинет')
        self.company = company
        self.NewError.setEnabled(False)
        self.UpdateError.setEnabled(False)
        self.initUI()

    def initUI(self):
        products = cur.execute(f'''SELECT title FROM {self.company}_Products''').fetchall()
        self.OrderProduct.addItems([elem[0] for elem in products])
        self.CatalogProduct.addItems([elem[0] for elem in products])
        data_table = cur.execute(f"SELECT * FROM {self.company}_Data").fetchall()
        products_table = cur.execute(f"SELECT * FROM {self.company}_Products").fetchall()
        if data_table:
            self.fill_table(data_table, self.OrderTable)
        if products_table:
            self.fill_table(products_table, self.ProductsTable)
            self.view_product_cost()
        self.CatalogProduct.textActivated.connect(self.view_product_cost)
        self.LoadNewButton.clicked.connect(self.load_new_product)
        self.DeleteButton.clicked.connect(self.delete)
        self.UpdateButton.clicked.connect(self.update_cost)
        self.AddOrder.clicked.connect(self.add_order)
        self.exitButton.clicked.connect(self.exit)

    # Функция для заполнения таблиц
    def fill_table(self, table, WidgetTable):
        WidgetTable.setRowCount(len(table))
        WidgetTable.setColumnCount(len(table[0]))
        for i, elem in enumerate(table):
            for j, val in enumerate(elem):
                WidgetTable.setItem(i, j, QTableWidgetItem(str(val)))

    def view_product_cost(self):
        price = cur.execute(f'''SELECT price FROM {self.company}_Products
                        WHERE title = "{self.CatalogProduct.currentText()}"''').fetchall()[0]
        self.Price.setText(str(price[0]))

    # Выход из личного кабинета
    def exit(self):
        valid = QMessageBox.question(
            self, '', f'Действительно выйти из личного кабинета?',
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            self.back = Enter()
            self.back.show()
            self.close()

    # Загрузка нового товара в каталог
    def load_new_product(self):
        self.NewError.setText("")
        if '"' in self.NewName.text():
            self.NewError.setText("Используйте одинарные ковычки")
            return
        product_not_new = cur.execute(f'''SELECT * FROM {self.company}_Products
                                        WHERE title = "{self.NewName.text()}"''').fetchall()
        # Проверяем введенный данные на корректность
        if product_not_new:
            self.NewError.setText("Продукт с таким наименованием\nуже есть в каталоге товаров")
            return
        if not self.NewPrice.text().isdigit():
            self.NewError.setText("В цене необходимо ввести только число")
            return
        cur.execute(f'''INSERT INTO {self.company}_Products(title, price)
                    VALUES ("{self.NewName.text()}",{self.NewPrice.text()})''')
        con.commit()
        rows = self.ProductsTable.rowCount()
        self.ProductsTable.setRowCount(rows + 1)
        self.ProductsTable.setItem(rows, 0, QTableWidgetItem(self.NewName.text()))
        self.ProductsTable.setItem(rows, 1, QTableWidgetItem(self.NewPrice.text()))
        self.OrderProduct.addItem(self.NewName.text())
        self.CatalogProduct.addItem(self.NewName.text())

    # Удалить товар из каталога
    def delete(self):
        valid = QMessageBox.question(
            self, '', f'Действительно удалить "{self.CatalogProduct.currentText()}?"',
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            cur.execute(f'''DELETE FROM {self.company}_Products
                            WHERE title = "{self.CatalogProduct.currentText()}"''')
            item = self.CatalogProduct.currentText()
            for row in range(self.ProductsTable.rowCount()):
                if self.ProductsTable.item(row, 0).text() == item:
                    self.ProductsTable.removeRow(row)
                    self.OrderProduct.removeItem(row)
                    self.CatalogProduct.removeItem(row)
                    break
            self.view_product_cost()
            con.commit()

    # Обновить цену на товар
    def update_cost(self):
        product_for_update = self.CatalogProduct.currentText()
        if not self.Price.text().isdigit():
            self.UpdateError.setText("В качестве цены укажите\nтолько цену в рублях")
            return
        cur.execute(f'''UPDATE {self.company}_Products
                        SET price = {int(self.Price.text())}
                        WHERE title = "{product_for_update}"''')
        for row in range(self.ProductsTable.rowCount()):
            if self.ProductsTable.item(row, 0).text() == product_for_update:
                self.ProductsTable.setItem(row, 1, QTableWidgetItem(self.Price.text()))
                break
        con.commit()

    # Совершить заказ
    def add_order(self):
        if not self.Quantity.text().isdigit():
            self.Quantity.setText("Укажите только число")
            return
        date = str(dt.datetime.now().date())
        product = self.OrderProduct.currentText()
        quantity = int(self.Quantity.text())
        cost = cur.execute(f'''SELECT price FROM {self.company}_Products
                                WHERE title = "{product}"''').fetchall()[0]
        cost = cost[0] * quantity
        cur.execute(f'''INSERT INTO {self.company}_Data
                    VALUES ("{product}", {quantity}, {cost}, "{date}")''')
        self.OrderTable.insertRow(0)
        self.OrderTable.setItem(0, 0, QTableWidgetItem(product))
        self.OrderTable.setItem(0, 1, QTableWidgetItem(str(quantity)))
        self.OrderTable.setItem(0, 2, QTableWidgetItem(str(cost)))
        self.OrderTable.setItem(0, 3, QTableWidgetItem(date))
        con.commit()
