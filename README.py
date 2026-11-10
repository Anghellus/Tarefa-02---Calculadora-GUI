# Tarefa-02---Calculadora-GUI
import ast
import math
import operator

import FreeSimpleGUI as sg


LIMITE_DISPLAY = 24
MAX_HISTORICO = 10


def calcular(expressao):
    """Avalia expressões aritméticas com operadores básicos."""
    operadores = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def avaliar(no):
        if isinstance(no, ast.Expression):
            return avaliar(no.body)
        if isinstance(no, ast.Constant) and type(no.value) in (int, float):
            return no.value
        if isinstance(no, ast.BinOp) and type(no.op) in operadores:
            return operadores[type(no.op)](avaliar(no.left), avaliar(no.right))
        if isinstance(no, ast.UnaryOp) and type(no.op) in operadores:
            return operadores[type(no.op)](avaliar(no.operand))
        raise ValueError("Expressão inválida")

    arvore = ast.parse(expressao, mode="eval")
    resultado = avaliar(arvore)
    if not math.isfinite(resultado):
        raise ValueError("Expressão inválida")
    return resultado


def ultimo_numero(expressao):
    if not expressao:
        return ""
    for operador in "+-*/":
        expressao = expressao.replace(operador, " ")
    partes = expressao.split()
    return partes[-1] if partes else ""


def inserir_caractere(expressao, valor):
    if not expressao:
        if valor in "+*/":
            return expressao
        if valor == "-":
            return valor

    if valor in "+-*/":
        if expressao[-1] in "+-*/":
            if valor == "-" and expressao[-1] in "+*/":
                return expressao + valor
            return expressao[:-1] + valor
        return expressao + valor

    if valor == ".":
        numero = ultimo_numero(expressao)
        if "." in numero:
            return expressao
        return expressao + valor

    return expressao + valor


class Calculadora:
    def __init__(self):
        self.expressao = ""
        self.resultado_exibido = False
        self.historico = []
        self.layout = self.criar_layout()
        self.janela = sg.Window("Calculadora", self.layout, finalize=True, font=("Segoe UI", 12), resizable=False)

    def criar_layout(self):
        botoes = [
            [sg.Button("7", size=(5, 2), key="7"), sg.Button("8", size=(5, 2), key="8"), sg.Button("9", size=(5, 2), key="9"), sg.Button("/", size=(5, 2), key="/")],
            [sg.Button("4", size=(5, 2), key="4"), sg.Button("5", size=(5, 2), key="5"), sg.Button("6", size=(5, 2), key="6"), sg.Button("*", size=(5, 2), key="*")],
            [sg.Button("1", size=(5, 2), key="1"), sg.Button("2", size=(5, 2), key="2"), sg.Button("3", size=(5, 2), key="3"), sg.Button("-", size=(5, 2), key="-")],
            [sg.Button("0", size=(5, 2), key="0"), sg.Button(".", size=(5, 2), key="."), sg.Button("←", size=(5, 2), key="backspace"), sg.Button("+", size=(5, 2), key="+")],
            [sg.Button("C", size=(11, 2), key="clear"), sg.Button("=", size=(11, 2), key="igual")],
        ]

        return [
            [sg.InputText(
                default_text="",
                key="-DISPLAY-",
                size=(20, 1),
                font=("Segoe UI", 24),
                justification="right",
                disabled=True,
            )],
            [sg.Column([botoes], justification="center")],
            [sg.Text("Histórico recente", font=("Segoe UI", 11, "bold"))],
            [sg.Listbox(values=[], select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, size=(30, 6), key="-HISTORICO-")],
        ]

    def atualizar_display(self, valor):
        texto = str(valor)[:LIMITE_DISPLAY]
        self.janela["-DISPLAY-"].update(texto)

    def tratar_erro(self, mensagem):
        self.atualizar_display(mensagem)
        self.resultado_exibido = True

    def adicionar_ao_historico(self, expressao, resultado):
        entrada = f"{expressao} = {resultado}"
        self.historico.append(entrada)
        self.historico = self.historico[-MAX_HISTORICO:]
        self.janela["-HISTORICO-"].update(values=list(reversed(self.historico)))

    def calcular_display(self):
        expressao = self.expressao.strip()
        if not expressao or len(expressao) > LIMITE_DISPLAY:
            self.tratar_erro("Erro: Expressão inválida")
            return
        if expressao[-1] in "+-*/":
            self.tratar_erro("Erro: Expressão inválida")
            return

        try:
            resultado = calcular(expressao)
        except ZeroDivisionError:
            self.tratar_erro("Erro: Divisão por zero")
            return
        except (ValueError, TypeError, SyntaxError, OverflowError):
            self.tratar_erro("Erro: Expressão inválida")
            return

        texto_resultado = format(resultado, ".12g")
        if len(texto_resultado) > LIMITE_DISPLAY:
            texto_resultado = texto_resultado[:LIMITE_DISPLAY]

        self.atualizar_display(texto_resultado)
        self.adicionar_ao_historico(expressao, texto_resultado)
        self.expressao = texto_resultado
        self.resultado_exibido = True

    def limpar(self):
        self.expressao = ""
        self.resultado_exibido = False
        self.atualizar_display("")
        self.historico.clear()
        self.janela["-HISTORICO-"].update(values=[])

    def apagar_ultimo(self):
        if self.expressao and not self.resultado_exibido:
            self.expressao = self.expressao[:-1]
            self.atualizar_display(self.expressao)
        elif self.resultado_exibido:
            self.expressao = ""
            self.resultado_exibido = False
            self.atualizar_display("")

    def processar_evento(self, event, values):
        if event in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "-", "*", "/", "."}:
            if self.resultado_exibido and event.isdigit() or (self.resultado_exibido and event == "."):
                self.expressao = ""
                self.resultado_exibido = False
            self.expressao = inserir_caractere(self.expressao, event)
            self.atualizar_display(self.expressao)
            return

        if event == "igual":
            self.calcular_display()
            return

        if event == "clear":
            self.limpar()
            return

        if event == "backspace":
            self.apagar_ultimo()
            return

    def executar(self):
        while True:
            event, values = self.janela.read()
            if event == sg.WIN_CLOSED:
                break
            self.processar_evento(event, values)

        self.janela.close()


def main():
    calculadora = Calculadora()
    calculadora.executar()


if __name__ == "__main__":
    main()
