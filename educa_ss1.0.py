import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLineEdit, QListWidget, QLabel, QMessageBox
)

conn = sqlite3.connect("escola.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS alunos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    nota1 REAL,
    nota2 REAL,
    frequencia INTEGER
)
""")

class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")

        layout = QVBoxLayout()

        self.usuario = QLineEdit()
        self.usuario.setPlaceholderText("Usuário")

        self.senha = QLineEdit()
        self.senha.setPlaceholderText("Senha")
        self.senha.setEchoMode(QLineEdit.Password)

        botao = QPushButton("Entrar")
        botao.clicked.connect(self.verificar_login)

        layout.addWidget(QLabel("Sistema Escolar"))
        layout.addWidget(self.usuario)
        layout.addWidget(self.senha)
        layout.addWidget(botao)

        self.setLayout(layout)

    def verificar_login(self):
        if self.usuario.text() == "admin" and self.senha.text() == "123":
            self.janela = App()
            self.janela.show()
            self.close()
        else:
            QMessageBox.warning(self, "Erro", "Login inválido!")

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema Escolar")

        layout = QVBoxLayout()

        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Nome do aluno")

        self.nota1 = QLineEdit()
        self.nota1.setPlaceholderText("Nota 1")

        self.nota2 = QLineEdit()
        self.nota2.setPlaceholderText("Nota 2")

        self.freq = QLineEdit()
        self.freq.setPlaceholderText("Frequência (%)")

        self.btn_add = QPushButton("Cadastrar")
        self.btn_add.clicked.connect(self.cadastrar)

        self.btn_delete = QPushButton("Excluir selecionado")
        self.btn_delete.clicked.connect(self.deletar)

        self.lista = QListWidget()

        layout.addWidget(self.input_nome)
        layout.addWidget(self.nota1)
        layout.addWidget(self.nota2)
        layout.addWidget(self.freq)
        layout.addWidget(self.btn_add)
        layout.addWidget(self.btn_delete)
        layout.addWidget(self.lista)

        self.setLayout(layout)

        self.listar()

    def cadastrar(self):
        nome = self.input_nome.text()

        try:
            n1 = float(self.nota1.text())
            n2 = float(self.nota2.text())
            freq = int(self.freq.text())
        except:
            QMessageBox.warning(self, "Erro", "Digite valores válidos!")
            return

        media = (n1 + n2) / 2

        cursor.execute("""
        INSERT INTO alunos (nome, nota1, nota2, frequencia)
        VALUES (?, ?, ?, ?)
        """, (nome, n1, n2, freq))

        conn.commit()

        self.input_nome.clear()
        self.nota1.clear()
        self.nota2.clear()
        self.freq.clear()

        self.listar()

    def listar(self):
        self.lista.clear()
        cursor.execute("SELECT id, nome, nota1, nota2, frequencia FROM alunos")

        for aluno in cursor.fetchall():
            id_, nome, n1, n2, freq = aluno

            if n1 is not None and n2 is not None:
                media = (n1 + n2) / 2
            else:
                media = 0

            status = "Aprovado" if media >= 7 and freq >= 75 else "Reprovado"

            self.lista.addItem(
                f"{id_} - {nome} | Média: {media:.1f} | Freq: {freq}% | {status}"
            )

    def deletar(self):
        item = self.lista.currentItem()
        if item:
            id_aluno = item.text().split(" - ")[0]
            cursor.execute("DELETE FROM alunos WHERE id=?", (id_aluno,))
            conn.commit()
            self.listar()
        else:
            QMessageBox.warning(self, "Erro", "Selecione um aluno!")

app = QApplication(sys.argv)
login = Login()
login.show()
sys.exit(app.exec_())
