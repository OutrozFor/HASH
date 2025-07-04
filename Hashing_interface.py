import tkinter as tk
from tkinter import messagebox
from Hashing import criar_dataset_teste, processar_dataset, salvar_csv, TabelaHashCPF
import random
# Importa as funções necessárias do módulo Hashing.py
# Variáveis globais para manter a tabela hash e clientes únicos
tabela = None
clientes_unicos = []

def executar():
    global tabela, clientes_unicos
    try:
        n = int(entry_qtd.get())
        d = float(entry_dup.get())
        if not (0 <= d < 1):
            raise ValueError
    except ValueError:
        messagebox.showerror("Erro", "Insira valores válidos!")
        return

    status_var.set("Gerando dados...")
    root.update()
    dataset = criar_dataset_teste(n_clientes=n, duplicatas=d)
    status_var.set("Processando...")
    root.update()
    clientes_unicos, estatisticas = processar_dataset(dataset)
    # Cria a tabela hash para buscas/remoções posteriores
    tabela = TabelaHashCPF()
    for cliente in clientes_unicos:
        tabela.inserir_cliente(cliente)
    salvar_csv(clientes_unicos, 'clientes_unicos.csv')
    status_var.set("Concluído! Arquivo 'clientes_unicos.csv' salvo.")

    msg = (
        f"Registros totais: {estatisticas['registros_totais']}\n"
        f"Clientes únicos: {estatisticas['clientes_unicos']}\n"
        f"Duplicatas removidas: {estatisticas['duplicatas_removidas']}\n"
        f"Colisões: {estatisticas['colisoes']}\n"
        f"Fator de carga: {estatisticas['fator_carga']:.2f}\n"
        f"Média por bucket: {estatisticas['media_por_bucket']:.2f}"
    )
    messagebox.showinfo("Estatísticas", msg)

def buscar_cliente():
    global tabela
    if tabela is None:
        messagebox.showwarning("Aviso", "Gere/processo os dados primeiro!")
        return
    cpf = entry_cpf.get()
    cliente = tabela.buscar_cliente(cpf)
    if cliente:
        msg = f"CPF: {cliente['cpf']}\nNome: {cliente['nome']}\nIdade: {cliente['idade']}\nCidade: {cliente['cidade']}"
        messagebox.showinfo("Cliente encontrado", msg)
    else:
        messagebox.showinfo("Cliente não encontrado", "Nenhum cliente com esse CPF.")

def remover_cliente():
    global tabela, clientes_unicos
    if tabela is None:
        messagebox.showwarning("Aviso", "Gere/processo os dados primeiro!")
        return
    cpf = entry_cpf.get()
    if tabela.remover_cliente(cpf):
        clientes_unicos = tabela.get_clientes_unicos()
        salvar_csv(clientes_unicos, 'clientes_unicos.csv')
        status_var.set("Cliente removido e arquivo atualizado.")
        messagebox.showinfo("Removido", "Cliente removido com sucesso!")
    else:
        messagebox.showinfo("Não encontrado", "Nenhum cliente com esse CPF.")

def listar_aleatorios():
    global clientes_unicos
    if not clientes_unicos:
        messagebox.showwarning("Aviso", "Gere/processo os dados primeiro!")
        return
    amostra = random.sample(clientes_unicos, min(10, len(clientes_unicos)))
    msg = ""
    for i, cliente in enumerate(amostra, 1):
        msg += f"{i}. {cliente['cpf']} | {cliente['nome']} | {cliente['idade']} | {cliente['cidade']}\n"
    messagebox.showinfo("10 Clientes Aleatórios", msg)

root = tk.Tk()
root.title("Remover Duplicatas de Clientes")

# Geração e processamento
tk.Label(root, text="Quantidade de clientes:").grid(row=0, column=0, sticky="e")
entry_qtd = tk.Entry(root)
entry_qtd.insert(0, "10000")
entry_qtd.grid(row=0, column=1)

tk.Label(root, text="Percentual de duplicatas (0 a 0.99):").grid(row=1, column=0, sticky="e")
entry_dup = tk.Entry(root)
entry_dup.insert(0, "0.1")
entry_dup.grid(row=1, column=1)

btn = tk.Button(root, text="Gerar e Processar", command=executar)
btn.grid(row=2, column=0, columnspan=2, pady=10)

# Busca e remoção por CPF
tk.Label(root, text="CPF para buscar/remover:").grid(row=3, column=0, sticky="e")
entry_cpf = tk.Entry(root)
entry_cpf.grid(row=3, column=1)

btn_buscar = tk.Button(root, text="Buscar Cliente", command=buscar_cliente)
btn_buscar.grid(row=4, column=0, pady=5)

btn_remover = tk.Button(root, text="Remover Cliente", command=remover_cliente)
btn_remover.grid(row=4, column=1, pady=5)

#listar clientes aleatórios
btn_listar = tk.Button(root, text="Listar 10 Aleatórios", command=listar_aleatorios)
btn_listar.grid(row=6, column=0, columnspan=2, pady=10)

status_var = tk.StringVar()
status_var.set("Aguardando...")
tk.Label(root, textvariable=status_var).grid(row=5, column=0, columnspan=2)

root.mainloop()
