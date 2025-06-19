import tkinter as tk
from tkinter import messagebox
import pandas as pd
import random

def carregar_perguntas():
    df = pd.read_excel("perguntas_gestao_operacoes.xlsx")
    df.columns = df.columns.str.strip()
    colunas_obrigatorias = ["Nível", "Pergunta", "A", "B", "C", "D", "Correta", "Explicacao"]
    for col in colunas_obrigatorias:
        if col not in df.columns:
            raise ValueError(f"Coluna obrigatória em falta: {col}")
    return df

def selecionar_perguntas(df):
    perguntas = []
    for nivel, n in [("Fácil", 3), ("Médio", 3), ("Difícil", 2)]:
        grupo = df[df["Nível"] == nivel]
        if len(grupo) < n:
            raise ValueError(f"Não há perguntas suficientes de nível {nivel}")
        perguntas += grupo.sample(n=n).to_dict("records")
    return perguntas

class MilionarioGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Quem Quer Ser um Gestor de Operações?")
        self.centrar_janela(self.master, 1000, 600)
        self.master.configure(bg="#001f3f")
        self.iniciar_jogo()

    def centrar_janela(self, janela, largura, altura):
        janela.update_idletasks()
        x = (janela.winfo_screenwidth() - largura) // 2
        y = (janela.winfo_screenheight() - altura) // 2
        janela.geometry(f"{largura}x{altura}+{x}+{y}")

    def iniciar_jogo(self):
        try:
            self.df = carregar_perguntas()
            self.perguntas = selecionar_perguntas(self.df)
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            self.master.quit()
            return

        self.indice = 0
        self.jogo_em_andamento = True
        self.ajuda_5050_usada = False
        self.ajuda_publico_usada = False
        self.ajuda_chamada_usada = False
        self.nivel_garantido = -1

        self.setup_interface()
        self.carregar_pergunta()

    def setup_interface(self):
        for widget in self.master.winfo_children():
            widget.destroy()

        self.frame_esquerda = tk.Frame(self.master, bg="#001f3f")
        self.frame_esquerda.pack(side="left", fill="y", padx=20)

        self.frame_centro = tk.Frame(self.master, bg="#001f3f")
        self.frame_centro.pack(side="left", fill="both", expand=True, padx=20)

        self.lbl_premios = []
        for valor in reversed(["1.000€", "2.000€", "5.000€", "10.000€", "30.000€", "50.000€", "100.000€", "250.000€"]):
            label = tk.Label(self.frame_esquerda, text=valor, font=("Helvetica", 14, "bold"),
                             bg="#001f3f", fg="white", anchor="w", width=12)
            label.pack(pady=3)
            self.lbl_premios.append(label)

        self.lbl_pergunta = tk.Label(self.frame_centro, text="", font=("Helvetica", 20, "bold"),
                                     wraplength=700, bg="#001f3f", fg="white", justify="center", pady=20)
        self.lbl_pergunta.pack(pady=20)

        self.btns = []
        for letra in ['A', 'B', 'C', 'D']:
            btn = tk.Button(self.frame_centro, text="", font=("Helvetica", 14, "bold"),
                            width=60, height=2, bg="#003366", fg="white", activebackground="#FFD700",
                            activeforeground="black", relief="raised",
                            command=lambda l=letra: self.verificar_resposta(l))
            btn.pack(pady=5)
            self.btns.append(btn)

        self.btn_ajuda_5050 = tk.Button(self.frame_centro, text="🔍 50/50", font=("Helvetica", 12, "bold"),
                                        bg="#FFA500", fg="black", width=10, command=self.usar_ajuda_5050)
        self.btn_ajuda_5050.pack(pady=5)

        self.btn_ajuda_publico = tk.Button(self.frame_centro, text="🔎 Público", font=("Helvetica", 12, "bold"),
                                           bg="#00CED1", fg="black", width=10, command=self.usar_ajuda_publico)
        self.btn_ajuda_publico.pack(pady=5)

        self.btn_ajuda_chamada = tk.Button(self.frame_centro, text="📱 Chamada", font=("Helvetica", 12, "bold"),
                                           bg="#90EE90", fg="black", width=10, command=self.usar_ajuda_chamada)
        self.btn_ajuda_chamada.pack(pady=5)

        self.btn_desistir = tk.Button(self.frame_centro, text="❌ Desistir", font=("Helvetica", 12, "bold"),
                                      bg="#FF6347", fg="black", width=10, command=self.desistir)
        self.btn_desistir.pack(pady=5)

    def atualizar_premios(self):
        for label in self.lbl_premios:
            label.config(bg="#001f3f", fg="white")
        if self.indice < len(self.lbl_premios):
            pos = len(self.lbl_premios) - 1 - self.indice
            self.lbl_premios[pos].config(bg="#FFD700", fg="black")

    def carregar_pergunta(self):
        if self.indice < len(self.perguntas):
            p = self.perguntas[self.indice]
            self.lbl_pergunta.config(text=p["Pergunta"])
            for i, letra in enumerate(['A', 'B', 'C', 'D']):
                self.btns[i].config(text=f"{letra}) {p[letra]}", state="normal")
            self.atualizar_premios()
        else:
            self.finalizar_jogo()

    def verificar_resposta(self, resposta):
        p = self.perguntas[self.indice]
        correta = p["Correta"]
        explicacao = p.get("Explicacao", "")
        self.mostrar_explicacao(resposta == correta, correta, explicacao)

    def mostrar_explicacao(self, certa, correta, explicacao):
        popup = tk.Toplevel(self.master)
        self.centrar_janela(popup, 600, 400)
        popup.title("Resultado")
        popup.configure(bg="#001f3f")

        titulo = "✅ Resposta Certa!" if certa else f"❌ Errado! A resposta correta era: {correta}"
        cor = "#00FF7F" if certa else "#FF6347"

        lbl_titulo = tk.Label(popup, text=titulo, font=("Helvetica", 18, "bold"), bg="#001f3f", fg=cor, wraplength=560)
        lbl_titulo.pack(pady=10)

        lbl_explicacao = tk.Label(popup, text=explicacao, font=("Helvetica", 14), wraplength=520,
                                  justify="left", bg="#001f3f", fg="white", pady=20)
        lbl_explicacao.pack(pady=10, padx=10)

        def continuar():
            popup.destroy()
            if certa:
                self.indice += 1
                self.carregar_pergunta()
            else:
                self.iniciar_jogo()

        btn = tk.Button(popup, text="Jogar novamente" if not certa else "Continuar", font=("Helvetica", 12),
                        bg="#003366", fg="white", command=continuar)
        btn.pack(pady=10)

    def usar_ajuda_5050(self):
        if self.ajuda_5050_usada:
            return
        self.ajuda_5050_usada = True
        correta = self.perguntas[self.indice]["Correta"]
        opcoes = ['A', 'B', 'C', 'D']
        opcoes.remove(correta)
        removidas = random.sample(opcoes, 2)
        for i, letra in enumerate(['A', 'B', 'C', 'D']):
            if letra in removidas:
                self.btns[i].config(state="disabled")

    def usar_ajuda_publico(self):
        if self.ajuda_publico_usada:
            return
        self.ajuda_publico_usada = True
        correta = self.perguntas[self.indice]["Correta"]
        votos = {letra: random.randint(10, 30) for letra in ['A', 'B', 'C', 'D']}
        votos[correta] += 30
        total = sum(votos.values())
        percentagens = {k: round(100 * v / total) for k, v in votos.items()}
        msg = "\n".join([f"{k}) {v}%" for k, v in percentagens.items()])
        messagebox.showinfo("Ajuda do Público", msg)

    def usar_ajuda_chamada(self):
        if self.ajuda_chamada_usada:
            return
        self.ajuda_chamada_usada = True
        correta = self.perguntas[self.indice]["Correta"]
        sugestao = f"Olha, eu acho que a resposta certa é a opção {correta}!"
        messagebox.showinfo("Ajuda por Chamada", sugestao)

    def desistir(self):
        if self.jogo_em_andamento:
            valor = ["1.000€", "2.000€", "5.000€", "10.000€", "30.000€", "50.000€", "100.000€", "250.000€"]
            premio = valor[self.nivel_garantido] if self.nivel_garantido >= 0 else "nenhum prêmio"
            jogar_novamente = messagebox.askyesno("Desistência", f"Conquistaste: {premio}\n\nQueres jogar novamente?")
            if jogar_novamente:
                self.iniciar_jogo()
            else:
                self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = MilionarioGUI(root)
    root.mainloop()
