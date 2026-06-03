import sys
import sqlite3
import random
import styles
import pandas as pd
import plotly.express as px

ESTILO_APP = styles.ESTILO_APP

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QMessageBox
)

from PyQt5.QtCore import Qt

def criar_botao(texto):

    botao = QPushButton(texto)

    botao.setMinimumHeight(45)

    return botao

# banco

conn = sqlite3.connect("escola.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS alunos(
id INTEGER PRIMARY KEY AUTOINCREMENT,
nome TEXT,
nota1 REAL,
nota2 REAL,
frequencia INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios(
id INTEGER PRIMARY KEY AUTOINCREMENT,
usuario TEXT,
senha TEXT,
tipo TEXT,
aluno_id INTEGER
)
""")

conn.commit()


# tela inicial

class TelaInicial(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("EDUCA.SS")

        self.resize(600, 500)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50,50,50,50)

        titulo = QLabel("EDUCA.SS")

        titulo.setAlignment(Qt.AlignCenter)

        titulo.setStyleSheet("""
        font-size:32px;
        font-weight:bold;
        color:#3498DB;
        padding:20px;
        """)

        btn_aluno = criar_botao("Entrar como Aluno")
        btn_prof = criar_botao("Entrar como Professor")
        btn_mentor = criar_botao("Entrar como Mentor")

        estilo = """
        QPushButton{
            font-size:18px;
            padding:15px;
        }
        """

        btn_aluno.setStyleSheet(estilo)
        btn_prof.setStyleSheet(estilo)
        btn_mentor.setStyleSheet(estilo)

        btn_aluno.clicked.connect(
            lambda: self.abrir_login("aluno")
        )

        btn_prof.clicked.connect(
            lambda: self.abrir_login("professor")
        )

        btn_mentor.clicked.connect(
            lambda: self.abrir_login("mentor")
        )

        layout.addWidget(titulo)

        layout.addWidget(btn_aluno)
        layout.addWidget(btn_prof)
        layout.addWidget(btn_mentor)

        self.setLayout(layout)

    def abrir_login(self, tipo):

        self.login = Login(tipo)

        self.login.show()

        self.close()


# login

class Login(QWidget):

    def __init__(self, tipo):

        super().__init__()

        self.tipo_esperado = tipo

        self.setWindowTitle("Login")

        self.resize(400, 300)

        layout = QVBoxLayout()

        titulo = QLabel(
            f"Login {tipo.capitalize()}"
        )

        titulo.setStyleSheet(
            "font-size:22px;"
        )

        self.usuario = QLineEdit()

        self.usuario.setPlaceholderText(
            "Usuário"
        )

        self.senha = QLineEdit()

        self.senha.setPlaceholderText(
            "Senha"
        )

        self.senha.setEchoMode(
            QLineEdit.Password
        )

        botao = QPushButton(
            "Entrar"
        )

        botao.clicked.connect(
            self.verificar
        )

        layout.addWidget(titulo)

        layout.addWidget(self.usuario)
        layout.addWidget(self.senha)
        layout.addWidget(botao)

        self.setLayout(layout)

    def verificar(self):

        usuario = self.usuario.text()

        senha = self.senha.text()

        cursor.execute("""
        SELECT tipo, aluno_id
        FROM usuarios
        WHERE usuario=?
        AND senha=?
        """, (usuario, senha))

        resultado = cursor.fetchone()

        if resultado:

            tipo = resultado[0]
            aluno_id = resultado[1]

            if tipo != self.tipo_esperado:

                QMessageBox.warning(
                    self,
                    "Erro",
                    "Tipo incorreto"
                )

                return

            if tipo == "aluno":

                self.janela = TelaAluno(
                    aluno_id
                )

            elif tipo == "professor":

                self.janela = TelaProfessor()

            elif tipo == "mentor":

                self.janela = TelaAdmin()

            self.janela.show()

            self.close()

        else:

            QMessageBox.warning(
                self,
                "Erro",
                "Login inválido"
            )

# tela aluno

class TelaAluno(QWidget):

    def __init__(self, id_aluno):

        super().__init__()

        self.resize(500, 400)

        layout = QVBoxLayout()

        self.info = QLabel()

        self.info.setStyleSheet("""
        font-size:18px;
        padding:15px;
        """)

        layout.addWidget(self.info)

        self.setLayout(layout)

        cursor.execute("""
        SELECT nome, nota1, nota2, frequencia
        FROM alunos
        WHERE id=?
        """, (id_aluno,))

        aluno = cursor.fetchone()

        nome, n1, n2, freq = aluno

        media = (n1 + n2) / 2

        status = "Aprovado"

        if media < 7 or freq < 75:
            status = "Reprovado"

        texto = f"""
Aluno: {nome}

Nota 1: {n1}
Nota 2: {n2}

Média: {media:.1f}

Frequência: {freq}%

Status: {status}
"""

        self.info.setText(texto)


# tela prof

class TelaProfessor(QWidget):

    def __init__(self):

        super().__init__()

        self.resize(700, 500)

        layout = QVBoxLayout()

        self.lista = QListWidget()

        self.lista.itemClicked.connect(
            self.selecionar_aluno
        )

        self.id_aluno = None

        self.n1 = QLineEdit()
        self.n1.setPlaceholderText(
            "Nota 1"
        )

        self.n2 = QLineEdit()
        self.n2.setPlaceholderText(
            "Nota 2"
        )

        self.freq = QLineEdit()
        self.freq.setPlaceholderText(
            "Frequência"
        )

        botao = QPushButton(
            "Atualizar"
        )

        botao.clicked.connect(
            self.atualizar
        )

        layout.addWidget(self.lista)
        layout.addWidget(self.n1)
        layout.addWidget(self.n2)
        layout.addWidget(self.freq)
        layout.addWidget(botao)

        self.setLayout(layout)

        self.listar()

    def listar(self):

        self.lista.clear()

        cursor.execute("""
        SELECT id, nome, nota1, nota2, frequencia
        FROM alunos
        """)

        for aluno in cursor.fetchall():

            id_, nome, n1, n2, freq = aluno

            media = (n1 + n2) / 2

            status = "Aprovado"

            if media < 7 or freq < 75:
                status = "Reprovado"

            texto = f"""
{nome} | Média: {media:.1f}
| Frequência: {freq}% | {status}
"""

            item = QListWidgetItem(texto)

            item.setSizeHint(item.sizeHint() * 2)

            # ID escondido
            item.setData(Qt.UserRole, id_)

            self.lista.addItem(item)

    def selecionar_aluno(self, item):

        self.id_aluno = item.data(
            Qt.UserRole
        )

        cursor.execute("""
        SELECT nota1, nota2, frequencia
        FROM alunos
        WHERE id=?
        """, (self.id_aluno,))

        aluno = cursor.fetchone()

        self.n1.setText(str(aluno[0]))
        self.n2.setText(str(aluno[1]))
        self.freq.setText(str(aluno[2]))

    def atualizar(self):

        cursor.execute("""
        UPDATE alunos
        SET nota1=?,
        nota2=?,
        frequencia=?
        WHERE id=?
        """, (
            self.n1.text(),
            self.n2.text(),
            self.freq.text(),
            self.id_aluno
        ))

        conn.commit()

        self.listar()

# dashboard

class Dashboard(QWidget):

    def __init__(self):

        super().__init__()

        self.resize(500,400)

        layout = QVBoxLayout()

        self.info = QLabel()

        layout.addWidget(self.info)

        self.setLayout(layout)

        self.carregar()

    def carregar(self):

        cursor.execute(
            "SELECT COUNT(*) FROM alunos"
        )

        total = cursor.fetchone()[0]

        cursor.execute("""
        SELECT nota1, nota2
        FROM alunos
        """)

        dados = cursor.fetchall()

        aprovados = 0

        for n1, n2 in dados:

            media = (n1+n2)/2

            if media >= 7:
                aprovados += 1

        reprovados = total - aprovados

        self.info.setText(f"""
Total de alunos: {total}

Aprovados: {aprovados}

Reprovados: {reprovados}
""")
        
        
def grafico_notas():

    cursor.execute("""
    SELECT nome, nota1, nota2
    FROM alunos
    """)

    dados = cursor.fetchall()

    df = pd.DataFrame(
        dados,
        columns=[
            "Nome",
            "Nota1",
            "Nota2"
        ]
    )

    fig = px.bar(
        df,
        x="Nome",
        y=["Nota1","Nota2"]
    )

    fig.show()


# tela adm

class TelaAdmin(QWidget):

    def __init__(self):

        super().__init__()

        self.resize(700, 700)

        layout = QVBoxLayout()

        dashboard = QPushButton(
            "Dashboard"
        )
        dashboard.clicked.connect(
            self.abrir_dashboard
        )

        layout.addWidget(dashboard)

        self.nome = QLineEdit()
        self.nome.setPlaceholderText(
            "Nome aluno"
        )

        self.n1 = QLineEdit()
        self.n1.setPlaceholderText(
            "Nota 1"
        )

        self.n2 = QLineEdit()
        self.n2.setPlaceholderText(
            "Nota 2"
        )

        self.freq = QLineEdit()
        self.freq.setPlaceholderText(
            "Frequência"
        )

        editar = QPushButton(
            "Atualizar Dados"
        )
        editar.clicked.connect(
            self.editar_aluno
        )

        grafico = QPushButton(
            "Gráfico de Notas"
        )

        grafico.clicked.connect(
            grafico_notas
        )

        aluno = QPushButton(
            "Cadastrar aluno"
        )

        aluno.clicked.connect(
            self.cadastrar_aluno
        )

        self.prof = QLineEdit()
        self.prof.setPlaceholderText(
            "Nome professor"
        )

        professor = QPushButton(
            "Cadastrar Professor"
        )

        professor.clicked.connect(
            self.cadastrar_professor
        )

        self.lista = QListWidget()

        self.pesquisa = QLineEdit()
        self.pesquisa.setPlaceholderText(
           "Pesquisar aluno..."
        )

        self.pesquisa.textChanged.connect(
        self.filtrar_alunos
        )

        excluir = QPushButton(
            "Excluir aluno"
        )

        excluir.clicked.connect(
            self.excluir
        )

        widgets = [
            self.nome,
            self.n1,
            self.n2,
            self.freq,
            editar,
            grafico,
            aluno,
            self.prof,
            professor,
            self.pesquisa,
            self.lista,
            excluir
        ]

        for item in widgets:
            layout.addWidget(item)

        self.setLayout(layout)

        self.listar()

    def cadastrar_aluno(self):

        cursor.execute("""
        INSERT INTO alunos(
        nome,
        nota1,
        nota2,
        frequencia
        )
        VALUES(?,?,?,?)
        """, (
            self.nome.text(),
            self.n1.text(),
            self.n2.text(),
            self.freq.text()
        ))

        conn.commit()

        aluno_id = cursor.lastrowid

        senha = str(
            random.randint(
                1000,
                9999
            )
        )

        cursor.execute("""
        INSERT INTO usuarios(
        usuario,
        senha,
        tipo,
        aluno_id
        )
        VALUES(?,?,?,?)
        """, (
            self.nome.text().lower(),
            senha,
            "aluno",
            aluno_id
        ))

        conn.commit()

        QMessageBox.information(
            self,
            "Aluno criado",
            f"Senha: {senha}"
        )

        self.nome.clear()
        self.n1.clear()
        self.n2.clear()
        self.freq.clear()

        self.listar()

    def cadastrar_professor(self):

        senha = str(
            random.randint(
                1000,
                9999
            )
        )

        cursor.execute("""
        INSERT INTO usuarios(
        usuario,
        senha,
        tipo
        )
        VALUES(?,?,?)
        """, (
            self.prof.text().lower(),
            senha,
            "professor"
        ))

        conn.commit()

        QMessageBox.information(
            self,
            "Professor criado",
            f"Senha: {senha}"
        )

        self.prof.clear()
        
    def editar_aluno(self):

        item = self.lista.currentItem()

        if not item:
            
            return
        
        id_aluno = item.data(Qt.UserRole)

        cursor.execute("""
        UPDATE alunos
        SET nome=?,
            nota1=?,
            nota2=?,
            frequencia=?
        WHERE id=?
        """, (
            self.nome.text(),
            self.n1.text(),
            self.n2.text(),
            self.freq.text(),
            id_aluno
        ))

        conn.commit()

        self.listar()


    def listar(self):

        self.lista.clear()

        cursor.execute("""
        SELECT id, nome, nota1, nota2, frequencia
        FROM alunos
        """)

        for aluno in cursor.fetchall():

            id_, nome, n1, n2, freq = aluno

            media = (n1 + n2) / 2

            status = "Aprovado"

            if media < 7 or freq < 75:
                status = "Reprovado"

            texto = f"""
{nome} | Média: {media:.1f}
| Frequência: {freq}% | {status}
"""

            item = QListWidgetItem(texto)

            item.setData(Qt.UserRole, id_)

            self.lista.addItem(item)

    def filtrar_alunos(self):

        texto = self.pesquisa.text().lower()

        for i in range(self.lista.count()):
            item = self.lista.item(i)

            item.setHidden(
                texto not in item.text().lower()
            )

    def excluir(self):

        item = self.lista.currentItem()

        if item:

            id_aluno = item.data(Qt.UserRole)

            cursor.execute(
                "DELETE FROM alunos WHERE id=?",
                (id_aluno,)
            )

            conn.commit()

            self.listar()

    def abrir_dashboard(self):

        self.dash = Dashboard()
        self.dash.show()


# adm padrao

cursor.execute("""
SELECT *
FROM usuarios
WHERE usuario='admin'
""")

if not cursor.fetchone():

    cursor.execute("""
    INSERT INTO usuarios(
    usuario,
    senha,
    tipo
    )
    VALUES(
    'athayde',
    '0192',
    'mentor'
    )
    """)

    conn.commit()


# .main

app = QApplication(sys.argv)

app.setStyleSheet(ESTILO_APP)

janela = TelaInicial()

janela.show()

sys.exit(app.exec_())