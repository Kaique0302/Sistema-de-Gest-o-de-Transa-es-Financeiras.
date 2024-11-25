import mysql.connector
import matplotlib.pyplot as plt
from datetime import datetime
import tkinter as tk
import pandas as pd
import os

# Função para criar uma conexão reutilizável
def conectar_banco():
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user=os.getenv("DB_USER", "root"),  # Usando variável de ambiente
            password=os.getenv("DB_PASSWORD", "kaiquegamer0302"),  # Usando variável de ambiente
            database="transações"
        )
        print("Conexão bem-sucedida!")
        return conexao
    except mysql.connector.Error as erro:
        print(f"Erro ao conectar ao banco de dados: {erro}")
        return None


# Função para inserir transação no banco
def inserir_transacao(tipo, valor, categoria, data, descricao):
    conexao = conectar_banco()
    if conexao:
        cursor = conexao.cursor()
        query = """
        INSERT INTO transacoes (tipo, valor, categoria, data, descricao)
        VALUES (%s, %s, %s, %s, %s)
        """
        valores = (tipo, valor, categoria, data, descricao)
        cursor.execute(query, valores)
        conexao.commit()
        print("Transação inserida com sucesso!")
        cursor.close()
        conexao.close()


def listar_transacoes():
    conexao = conectar_banco()
    if conexao:
        cursor = conexao.cursor()
        query = "SELECT * FROM transacoes"
        cursor.execute(query)
        resultados = cursor.fetchall()

        # Verificando se há dados retornados
        if len(resultados) == 0:
            print("Nenhuma transação encontrada!")
        else:
            print(f"{len(resultados)} transações encontradas.")
            for transacao in resultados:
                print(transacao)  # Exibe cada transação

        cursor.close()
        conexao.close()

        # Retornando o DataFrame com os resultados
        return pd.DataFrame(resultados, columns=["id", "tipo", "valor", "categoria", "data", "descricao"])
    else:
        print("Erro na conexão com o banco.")
        return None


# Função para buscar transações por categoria
def buscar_transacoes_por_categoria(categoria):
    conexao = conectar_banco()
    if conexao:
        cursor = conexao.cursor()
        query = "SELECT * FROM transacoes WHERE categoria = %s"
        cursor.execute(query, (categoria,))
        resultados = cursor.fetchall()
        cursor.close()
        conexao.close()
        return pd.DataFrame(resultados, columns=["id", "tipo", "valor", "categoria", "data", "descricao"])


# Função para gerar o resumo por categoria
def resumo_por_categoria():
    conn = conectar_banco()
    cursor = conn.cursor()
    query = "SELECT categoria, SUM(valor) FROM transacoes GROUP BY categoria"
    cursor.execute(query)
    resultados = cursor.fetchall()
    conn.close()
    return pd.DataFrame(resultados, columns=["Categoria", "Total"])


# Função para calcular o saldo por data
def saldo_por_data():
    conn = conectar_banco()
    cursor = conn.cursor()
    query = """
        SELECT data, SUM(CASE WHEN tipo='Receita' THEN valor ELSE -valor END) as saldo
        FROM transacoes
        GROUP BY data
        ORDER BY data
    """
    cursor.execute(query)
    resultados = cursor.fetchall()
    conn.close()
    return pd.DataFrame(resultados, columns=["Data", "Saldo"])


# Função para calcular a média mensal de receitas e despesas
def calcular_media_mensal():
    transacoes = listar_transacoes()
    
    transacoes["data"] = pd.to_datetime(transacoes["data"], format="%d/%m/%Y")
    transacoes["mes"] = transacoes["data"].dt.to_period("M")
    
    receitas = transacoes[transacoes["tipo"] == "Receita"]
    despesas = transacoes[transacoes["tipo"] == "Despesa"]
    
    media_receitas = receitas.groupby("mes")["valor"].sum().mean()
    media_despesas = despesas.groupby("mes")["valor"].sum().mean()
    
    return media_receitas, media_despesas


# Função para projetar finanças futuras
def projetar_financas(meses=12, taxa_crescimento=0.05):
    media_receitas, media_despesas = calcular_media_mensal()
    
    meses_futuros = [f"Mês {i+1}" for i in range(meses)]
    receitas_futuras = [media_receitas * (1 + taxa_crescimento) ** i for i in range(meses)]
    despesas_futuras = [media_despesas * (1 + taxa_crescimento) ** i for i in range(meses)]
    
    return meses_futuros, receitas_futuras, despesas_futuras
