
from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import pandas as pd
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    despesas = conn.execute('SELECT * FROM despesas').fetchall()
    receitas = conn.execute('SELECT * FROM receitas').fetchall()
    conn.close()
    saldo = sum([r['valor_total'] for r in receitas]) - sum([d['valor_total'] for d in despesas])
    return render_template('index.html', despesas=despesas, receitas=receitas, saldo=saldo)

@app.route('/add-despesa', methods=['POST'])
def add_despesa():
    dados = (
        request.form['vencimento'],
        request.form['descricao'],
        request.form['categoria'],
        request.form['parcela'],
        request.form['data_quitacao'],
        float(request.form['valor_parcela']),
        float(request.form['desconto']),
        float(request.form['juros']),
        float(request.form['valor_total'])
    )
    conn = get_db_connection()
    conn.execute("""INSERT INTO despesas
        (vencimento, descricao, categoria, parcela, data_quitacao,
        valor_parcela, desconto, juros, valor_total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", dados)
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/add-receita', methods=['POST'])
def add_receita():
    dados = (
        request.form['vencimento'],
        request.form['cliente'],
        request.form['nota_fiscal'],
        request.form['data_quitacao'],
        float(request.form['valor_nf']),
        float(request.form['desconto']),
        float(request.form['juros']),
        float(request.form['valor_total'])
    )
    conn = get_db_connection()
    conn.execute("""INSERT INTO receitas
        (vencimento, cliente, nota_fiscal, data_quitacao,
        valor_nf, desconto, juros, valor_total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", dados)
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/exportar')
def exportar():
    conn = get_db_connection()
    despesas = pd.read_sql_query("SELECT * FROM despesas", conn)
    receitas = pd.read_sql_query("SELECT * FROM receitas", conn)
    with pd.ExcelWriter("/mnt/data/controle_financeiro.xlsx") as writer:
        despesas.to_excel(writer, sheet_name="Despesas", index=False)
        receitas.to_excel(writer, sheet_name="Receitas", index=False)
    conn.close()
    return send_file("/mnt/data/controle_financeiro.xlsx", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
