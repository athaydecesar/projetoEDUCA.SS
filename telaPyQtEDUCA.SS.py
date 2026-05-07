import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit ,QListWidget

conn = sqlite3.connect("escola2.db")
cursor = conn.cursor()

cursor.execute("""
               CREATE TABLE IF NOT EXISTS alunos(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               nome TEXT
               )
               """)

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EDUCA.SS - PyQt")

        self.layout = QVBoxLayout()

        self.input_nome = QLineEdit()
        self.layout.addWidget(self.input_nome)

        self.botao = QPushButton("Cadastrar")
        self.botao.clicked.connect(self.cadastrar)
        self.layout.addWidget(self.botao)

        self.lista = QListWidget()
        self.layout.addWidget(self.lista)

        self.setLayout(self.layout)

        self.listar()

    def cadastrar(self):
        nome = self.input_nome.text()
        cursor.execute("INSERT INTO alunos (nome) VALUES (?)", (nome,))
        conn.commit()
        self.input_nome.clear()
        self.listar()

    def listar(self):
        self.lista.clear()
        cursor.execute("SELECT nome FROM alunos")
        for aluno in cursor.fetchall():
            self.lista.addItem(aluno[0])

app = QApplication(sys.argv)
janela = App()
janela.show()
sys.exit(app.exec_())
