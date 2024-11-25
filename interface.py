import tkinter as tk
from tkinter import ttk, messagebox
from database import inserir_transacao, listar_transacoes, projetar_financas, saldo_por_data
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np


def adicionar_transacao():
    tipo = tipo_var.get()
    valor = float(valor_entry.get())
    categoria = categoria_entry.get()
    data = data_entry.get()
    descricao = descricao_entry.get()

    # Conversão de data
    try:
        data_formatada = datetime.strptime(data, '%d/%m/%Y').strftime('%Y-%m-%d')
    except ValueError:
        messagebox.showerror("Erro", "Data inválida! Use o formato DD/MM/YYYY.")
        return

    # Tentativa de inserir no banco
    try:
        inserir_transacao(tipo, valor, categoria, data_formatada, descricao)
        messagebox.showinfo("Sucesso", "Transação adicionada com sucesso!")
        limpar_campos()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao inserir transação: {e}")


def exibir_transacoes():
    transacoes = listar_transacoes()
    if transacoes is not None:
        for row in transacoes.itertuples():
            tree.insert("", "end", values=row[1:])


def limpar_campos():
    tipo_var.set("")
    valor_entry.delete(0, tk.END)
    categoria_entry.delete(0, tk.END)
    data_entry.delete(0, tk.END)
    descricao_entry.delete(0, tk.END)


# Função para verificar se o valor é numérico
def is_numeric(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def grafico_por_categoria():
    # Pega as transações do banco de dados
    transacoes = listar_transacoes()  # Função que retorna as transações do banco

    # Processa as transações por categoria
    categorias = {}
    for row in transacoes.itertuples():
        categoria = row[3]  # A categoria está na coluna 3 (ajuste conforme necessário)
        valor = row[2]  # O valor está na coluna 2 (ajuste conforme necessário)
        
        try:
            valor = float(valor)  # Converte o valor para float, se possível
        except ValueError:
            continue  # Caso o valor não possa ser convertido, pula a transação

        if categoria not in categorias:
            categorias[categoria] = 0
        categorias[categoria] += valor

    # Gerar gráfico com as categorias
    grafico_window = tk.Toplevel(janela)
    grafico_window.title("Gráfico de Distribuição de Gastos por Categoria")
    
    # Criar gráfico de pizza
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(list(categorias.values()), labels=list(categorias.keys()), autopct='%1.1f%%', startangle=140)
    ax.set_title("Distribuição de Gastos por Categoria")

    # Exibir gráfico no Tkinter
    canvas = FigureCanvasTkAgg(fig, master=grafico_window)
    canvas.draw()
    canvas.get_tk_widget().pack()



def grafico_saldo_tempo():
    dados = saldo_por_data()
    datas = [item[0] for item in dados]
    saldos = [item[1] for item in dados]

    # Criando uma nova janela para o gráfico
    grafico_window = tk.Toplevel(janela)
    grafico_window.title("Gráfico de Saldo ao Longo do Tempo")

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(datas, saldos, marker='o')
    ax.set_title("Evolução do Saldo ao Longo do Tempo")
    ax.set_xlabel("Data")
    ax.set_ylabel("Saldo (R$)")
    ax.grid()

    # Criar canvas para o gráfico no Tkinter
    canvas = FigureCanvasTkAgg(fig, master=grafico_window)
    canvas.draw()
    canvas.get_tk_widget().pack()


def gerar_grafico_projecao(meses_futuros, receitas_futuras, despesas_futuras):
    print("Gerando gráfico com os seguintes dados:")
    print("Meses:", meses_futuros)
    print("Receitas:", receitas_futuras)
    print("Despesas:", despesas_futuras)
    
    if not meses_futuros or not receitas_futuras or not despesas_futuras:
        print("Dados insuficientes para gerar o gráfico")
        return

    fig, ax = plt.subplots()
    
    # Plotando as receitas e despesas projetadas
    ax.plot(meses_futuros, receitas_futuras, label="Receitas", color="green", marker="o")
    ax.plot(meses_futuros, despesas_futuras, label="Despesas", color="red", marker="o")
    
    ax.set_xlabel('Meses Futuros')
    ax.set_ylabel('Valor (R$)')
    ax.set_title('Projeção Financeira Futura')
    ax.legend()
    
    # Exibindo o gráfico
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def relatorio_projecao():
    meses_futuros, receitas_futuras, despesas_futuras = projetar_financas()
    
    # Verifique os dados
    print("Meses Futuros:", meses_futuros)
    print("Receitas Futuros:", receitas_futuras)
    print("Despesas Futuros:", despesas_futuras)
    
    if meses_futuros and receitas_futuras and despesas_futuras:
        gerar_grafico_projecao(meses_futuros, receitas_futuras, despesas_futuras)
    else:
        messagebox.showerror("Erro", "Não há dados suficientes para gerar o gráfico.")


# Configurar Janela Principal
janela = tk.Tk()
janela.title("Gerenciador de Finanças")

# Widgets para adicionar transações
tipo_var = tk.StringVar()
ttk.Label(janela, text="Tipo:").grid(row=0, column=0, pady=5)
ttk.Combobox(janela, textvariable=tipo_var, values=["Receita", "Despesa"]).grid(row=0, column=1, pady=5)

ttk.Label(janela, text="Valor:").grid(row=1, column=0, pady=5)
valor_entry = ttk.Entry(janela)
valor_entry.grid(row=1, column=1, pady=5)

ttk.Label(janela, text="Categoria:").grid(row=2, column=0, pady=5)
categoria_entry = ttk.Entry(janela)
categoria_entry.grid(row=2, column=1, pady=5)

ttk.Label(janela, text="Data:").grid(row=3, column=0, pady=5)
data_entry = ttk.Entry(janela)
data_entry.grid(row=3, column=1, pady=5)

ttk.Label(janela, text="Descrição:").grid(row=4, column=0, pady=5)
descricao_entry = ttk.Entry(janela)
descricao_entry.grid(row=4, column=1, pady=5)

ttk.Button(janela, text="Adicionar Transação", command=adicionar_transacao).grid(row=5, column=0, pady=10)
ttk.Button(janela, text="Exibir Transações", command=exibir_transacoes).grid(row=5, column=1, pady=10)

# Exibição de Transações
tree = ttk.Treeview(janela, columns=("ID", "Tipo", "Valor", "Categoria", "Data", "Descrição"), show="headings")
tree.grid(row=6, column=0, columnspan=2, pady=10)

tree.heading("ID", text="ID")
tree.heading("Tipo", text="Tipo")
tree.heading("Valor", text="Valor")
tree.heading("Categoria", text="Categoria")
tree.heading("Data", text="Data")
tree.heading("Descrição", text="Descrição")



# Botões para Gráficos
botao_grafico_categoria = ttk.Button(janela, text="Gráfico por Categoria", command=grafico_por_categoria)
botao_grafico_categoria.grid(row=7, column=0, pady=10)

botao_grafico_saldo = ttk.Button(janela, text="Gráfico de Saldo", command=grafico_saldo_tempo)
botao_grafico_saldo.grid(row=7, column=1, pady=10)

botao_projecao = ttk.Button(janela, text="Projeção Financeira", command=relatorio_projecao)
botao_projecao.grid(row=8, column=0, columnspan=2, pady=10)

janela.mainloop()
