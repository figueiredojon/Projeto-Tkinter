import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

con = sqlite3.connect("clinica_simples.db")
cur = con.cursor()
cur.execute("PRAGMA foreign_keys = ON")

cur.execute("""
CREATE TABLE IF NOT EXISTS medico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    especialidade TEXT NOT NULL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS paciente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    nascimento TEXT NOT NULL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS consulta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    horario TEXT NOT NULL,
    medico_id INTEGER NOT NULL,
    paciente_id INTEGER NOT NULL,
    FOREIGN KEY(medico_id) REFERENCES medico(id) ON DELETE CASCADE,
    FOREIGN KEY(paciente_id) REFERENCES paciente(id) ON DELETE CASCADE
)
""")
con.commit()

root = tk.Tk()
root.title("Clínica Médica - CRUD")
root.geometry("900x520")

abas = ttk.Notebook(root)
abas.pack(fill="both", expand=True)

frm_med = ttk.Frame(abas)
abas.add(frm_med, text="Médicos")

m_nome = tk.Entry(frm_med, width=40)
m_esp = tk.Entry(frm_med, width=40)

tk.Label(frm_med, text="Nome do Médico:").pack(pady=2)
m_nome.pack()
tk.Label(frm_med, text="Especialidade:").pack(pady=2)
m_esp.pack()

cols_m = ("ID", "Nome", "Especialidade")
tv_med = ttk.Treeview(frm_med, columns=cols_m, show="headings", height=10)
for c in cols_m:
    tv_med.heading(c, text=c)
tv_med.pack(fill="both", expand=True, pady=10)

def atualizar_medicos():
    tv_med.delete(*tv_med.get_children())
    for r in cur.execute("SELECT * FROM medico ORDER BY id DESC").fetchall():
        tv_med.insert("", tk.END, values=r)

def add_medico():
    nome = m_nome.get().strip()
    esp = m_esp.get().strip()
    if nome == "" or esp == "":
        messagebox.showwarning("Aviso", "Preencha todos os campos!")
        return
    cur.execute("INSERT INTO medico(nome, especialidade) VALUES (?,?)", (nome, esp))
    con.commit()
    m_nome.delete(0, tk.END)
    m_esp.delete(0, tk.END)
    atualizar_medicos()

def help():
    messagebox.showinfo(
        title="Informação do Projeto",
        message=("Desenvolvido por: Eduardo Ramos, Danilo Cavalcante, Jonatas Figueiredo. "
                    "Este projeto é um CRUD básico para uma clínica médica, "
                    "desenvolvido usando SQLite e Tkinter."                
                 )
    )

btn_add_m = tk.Button(frm_med, text="Salvar Médico", command=add_medico)
btn_add_m.pack(pady=5)

help = tk.Button(frm_med, text="Ajuda", command=help)
help.pack(pady=5)

frm_pac = ttk.Frame(abas)
abas.add(frm_pac, text="Pacientes")

p_nome = tk.Entry(frm_pac, width=40)
p_nasc = tk.Entry(frm_pac, width=40)

tk.Label(frm_pac, text="Nome do Paciente:").pack(pady=2)
p_nome.pack()
tk.Label(frm_pac, text="Nascimento (dd/mm/aaaa):").pack(pady=2)
p_nasc.pack()

cols_p = ("ID", "Nome", "Nascimento")
tv_pac = ttk.Treeview(frm_pac, columns=cols_p, show="headings", height=10)
for c in cols_p:
    tv_pac.heading(c, text=c)
tv_pac.pack(fill="both", expand=True, pady=10)

def atualizar_pacientes():
    tv_pac.delete(*tv_pac.get_children())
    for r in cur.execute("SELECT * FROM paciente ORDER BY id DESC").fetchall():
        tv_pac.insert("", tk.END, values=r)

def add_paciente():
    nome = p_nome.get().strip()
    nasc = p_nasc.get().strip()
    if nome == "" or nasc == "":
        messagebox.showwarning("Aviso", "Preencha todos os campos!")
        return
    cur.execute("INSERT INTO paciente(nome, nascimento) VALUES (?,?)", (nome, nasc))
    con.commit()
    p_nome.delete(0, tk.END)
    p_nasc.delete(0, tk.END)
    atualizar_pacientes()

btn_add_p = tk.Button(frm_pac, text="Salvar Paciente", command=add_paciente)
btn_add_p.pack(pady=5)

frm_con = ttk.Frame(abas)
abas.add(frm_con, text="Consultas")

c_data = tk.Entry(frm_con, width=20)
c_hora = tk.Entry(frm_con, width=20)
c_med = ttk.Combobox(frm_con, width=40, state="readonly")
c_pac = ttk.Combobox(frm_con, width=40, state="readonly")

tk.Label(frm_con, text="Data (dd/mm/aaaa):").pack(pady=2)
c_data.pack()
tk.Label(frm_con, text="Horário (HH:MM):").pack(pady=2)
c_hora.pack()
tk.Label(frm_con, text="Médico:").pack(pady=2)
c_med.pack()
tk.Label(frm_con, text="Paciente:").pack(pady=2)
c_pac.pack()

cols_c = ("ID", "Data", "Hora", "Médico", "Paciente")
tv_con = ttk.Treeview(frm_con, columns=cols_c, show="headings", height=12)
for c in cols_c:
    tv_con.heading(c, text=c)
tv_con.pack(fill="both", expand=True, pady=10)

def atualizar_consultas():
    c_med["values"] = [f"{m[0]} - {m[1]}" for m in cur.execute("SELECT * FROM medico").fetchall()]
    c_pac["values"] = [f"{p[0]} - {p[1]}" for p in cur.execute("SELECT * FROM paciente").fetchall()]

    tv_con.delete(*tv_con.get_children())
    for r in cur.execute("""
        SELECT consulta.id, consulta.data, consulta.horario, medico.nome, paciente.nome 
        FROM consulta 
        JOIN medico ON medico.id = consulta.medico_id 
        JOIN paciente ON paciente.id = consulta.paciente_id 
        ORDER BY data, horario
    """).fetchall():
        tv_con.insert("", tk.END, values=r)

def add_consulta():
    if not c_data.get() or not c_hora.get() or not c_med.get() or not c_pac.get():
        messagebox.showwarning("Aviso", "Preencha tudo!")
        return

    med_id = int(c_med.get().split(" - ")[0])
    pac_id = int(c_pac.get().split(" - ")[0])

    cur.execute("INSERT INTO consulta(data, horario, medico_id, paciente_id) VALUES (?,?,?,?)",
                (c_data.get(), c_hora.get(), med_id, pac_id))
    con.commit()

    atualizar_consultas()

btn_add_con = tk.Button(frm_con, text="Agendar Consulta", command=add_consulta)
btn_add_con.pack(pady=5)

def on_tab_change(event):
    aba_atual = event.widget.tab(event.widget.index("current"))["text"]

    if aba_atual == "Médicos":
        atualizar_medicos()
    elif aba_atual == "Pacientes":
        atualizar_pacientes()
    elif aba_atual == "Consultas":
        atualizar_consultas()

abas.bind("<<NotebookTabChanged>>", on_tab_change)

atualizar_medicos()
atualizar_pacientes()
atualizar_consultas()

root.mainloop()
con.close()
