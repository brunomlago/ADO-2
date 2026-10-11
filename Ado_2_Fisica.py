"""
ADO 2 - Leis de Newton e Aplicacoes

Dependencias:
    pip install numpy matplotlib
"""

import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

G = 9.81  # aceleracao da gravidade em m/s^2


class SimuladorFisica:
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("ADO 2 - Leis de Newton e Aplicacoes")
        self.raiz.geometry("1200x760")
        self.raiz.minsize(1050, 680)

        self.sistema = tk.StringVar(value="Plano inclinado")
        self.modo_arrasto = tk.StringVar(value="Linear")
        self.parametros = {}
        self.sliders = {}
        self._tarefa_atualizacao = None
        self._atraso_atualizacao_ms = 35

        self._montar_interface()
        self._configurar_sistema()

    def _montar_interface(self):
        topo = ttk.Frame(self.raiz, padding=10)
        topo.pack(fill=tk.X)

        ttk.Label(topo, text="Sistema fisico:", font=("Arial", 11, "bold")).pack(side=tk.LEFT)
        seletor = ttk.Combobox(
            topo,
            textvariable=self.sistema,
            values=["Plano inclinado", "Forca centripeta", "Forca de arrasto"],
            state="readonly",
            width=24,
        )
        seletor.pack(side=tk.LEFT, padx=8)
        seletor.bind("<<ComboboxSelected>>", lambda _e: self._configurar_sistema())

        ttk.Button(topo, text="Restaurar valores", command=self._configurar_sistema).pack(side=tk.RIGHT)

        corpo = ttk.Frame(self.raiz, padding=(10, 0, 10, 10))
        corpo.pack(fill=tk.BOTH, expand=True)

        self.painel_controles = ttk.LabelFrame(corpo, text="Parametros", padding=12)
        self.painel_controles.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.figura = Figure(figsize=(8.2, 6.2), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figura, master=corpo)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.rotulo_resultados = ttk.Label(
            self.painel_controles,
            text="",
            justify=tk.LEFT,
            font=("Consolas", 10),
            foreground="#143d59",
        )

    def _limpar_controles(self):
        for componente in self.painel_controles.winfo_children():
            componente.destroy()
        self.parametros.clear()
        self.sliders.clear()

    def _adicionar_slider(self, chave, texto, minimo, maximo, inicial, resolucao=0.1, unidade=""):
        bloco = ttk.Frame(self.painel_controles)
        bloco.pack(fill=tk.X, pady=5)

        valor = tk.DoubleVar(value=inicial)
        self.parametros[chave] = valor

        cabecalho = ttk.Frame(bloco)
        cabecalho.pack(fill=tk.X)
        ttk.Label(cabecalho, text=texto).pack(side=tk.LEFT)
        indicador = ttk.Label(cabecalho, width=12, anchor=tk.E)
        indicador.pack(side=tk.RIGHT)

        escala = tk.Scale(
            bloco,
            from_=minimo,
            to=maximo,
            resolution=resolucao,
            orient=tk.HORIZONTAL,
            variable=valor,
            showvalue=False,
            length=270,
            command=lambda _v: self._ao_mover_slider(),
        )
        escala.pack(fill=tk.X)
        self.sliders[chave] = (indicador, unidade)

    def _atualizar_indicadores(self):
        for chave, (rotulo, unidade) in self.sliders.items():
            rotulo.config(text=f"{self.parametros[chave].get():.2f} {unidade}")

    def _ao_mover_slider(self):
        """Atualiza o numero imediatamente e limita a frequencia dos graficos."""
        self._atualizar_indicadores()
        self._agendar_atualizacao()

    def _agendar_atualizacao(self):
        """Debounce: evita redesenhar o Matplotlib a cada pixel do mouse."""
        if self._tarefa_atualizacao is not None:
            self.raiz.after_cancel(self._tarefa_atualizacao)
        self._tarefa_atualizacao = self.raiz.after(
            self._atraso_atualizacao_ms, self._executar_atualizacao_agendada
        )

    def _executar_atualizacao_agendada(self):
        self._tarefa_atualizacao = None
        self._atualizar()

    def _configurar_sistema(self):
        self._limpar_controles()
        sistema = self.sistema.get()

        if sistema == "Plano inclinado":
            self._adicionar_slider("m1", "Massa no plano (m1)", 0.5, 15.0, 5.0, 0.1, "kg")
            self._adicionar_slider("m2", "Massa pendurada (m2)", 0.5, 15.0, 3.0, 0.1, "kg")
            self._adicionar_slider("theta", "Angulo do plano", 0.0, 80.0, 25.0, 1.0, "graus")
            self._adicionar_slider("mus", "Atrito estatico (mu_s)", 0.0, 1.0, 0.20, 0.01, "")
            self._adicionar_slider("muk", "Atrito cinetico (mu_k)", 0.0, 1.0, 0.15, 0.01, "")
            self._adicionar_slider("v0", "Velocidade inicial", -5.0, 5.0, 0.0, 0.1, "m/s")
            self._adicionar_slider("tempo", "Tempo de simulacao", 2.0, 20.0, 10.0, 0.5, "s")

        elif sistema == "Forca centripeta":
            self._adicionar_slider("m", "Massa", 0.1, 20.0, 2.0, 0.1, "kg")
            self._adicionar_slider("R", "Raio", 0.2, 10.0, 3.0, 0.1, "m")
            self._adicionar_slider("v", "Velocidade tangencial", 0.1, 20.0, 5.0, 0.1, "m/s")
            self._adicionar_slider("tempo", "Tempo de simulacao", 2.0, 20.0, 10.0, 0.5, "s")

        else:
            ttk.Label(self.painel_controles, text="Modelo de arrasto:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
            for texto in ("Linear", "Quadratico"):
                ttk.Radiobutton(
                    self.painel_controles,
                    text=texto,
                    value=texto,
                    variable=self.modo_arrasto,
                    command=self._agendar_atualizacao,
                ).pack(anchor=tk.W)
            ttk.Separator(self.painel_controles).pack(fill=tk.X, pady=7)
            self._adicionar_slider("m", "Massa", 0.1, 20.0, 2.0, 0.1, "kg")
            self._adicionar_slider("coef", "Coeficiente b ou c", 0.05, 5.0, 0.80, 0.05, "")
            self._adicionar_slider("tempo", "Tempo de simulacao", 2.0, 30.0, 12.0, 0.5, "s")

        self.rotulo_resultados = ttk.Label(
            self.painel_controles,
            text="",
            justify=tk.LEFT,
            font=("Consolas", 10),
            foreground="#143d59",
        )
        self.rotulo_resultados.pack(fill=tk.X, pady=(16, 4))
        self._atualizar()

    def _atualizar(self):
        # O redesenho ocorre no maximo uma vez por janela de debounce.
        self._atualizar_indicadores()
        if self.sistema.get() == "Plano inclinado":
            self._plotar_plano_inclinado()
        elif self.sistema.get() == "Forca centripeta":
            self._plotar_centripeta()
        else:
            self._plotar_arrasto()
        self.canvas.draw_idle()

    def _plotar_plano_inclinado(self):
        m1 = self.parametros["m1"].get()
        m2 = self.parametros["m2"].get()
        theta = np.deg2rad(self.parametros["theta"].get())
        mu_s = self.parametros["mus"].get()
        mu_k = self.parametros["muk"].get()
        v0 = self.parametros["v0"].get()
        tf = self.parametros["tempo"].get()
        t = np.linspace(0.0, tf, 360)

        # Perpendicularmente ao plano nao ha aceleracao: N = m1*g*cos(theta).
        normal = m1 * G * np.cos(theta)
        # Forca que tende a mover o conjunto, positiva quando m2 desce.
        f_motriz = m2 * G - m1 * G * np.sin(theta)
        limite_estatico = mu_s * normal

        if abs(f_motriz) <= limite_estatico and abs(v0) < 1e-12:
            a = 0.0
            estado = "EQUILIBRIO ESTATICO"
            # Em repouso, para m2: T = m2*g.
            tracao = m2 * G
        else:
            # O atrito cinetico tem sentido contrario a tendencia de movimento.
            sinal = np.sign(f_motriz)
            a = (f_motriz - mu_k * normal * sinal) / (m1 + m2)
            estado = "MOVIMENTO"
            # Pela 2a Lei aplicada a m2, adotando para baixo como positivo:
            # m2*g - T = m2*a  =>  T = m2*(g-a).
            tracao = m2 * (G - a)

        # MRUV: formulas fechadas, sem integracao numerica.
        x = v0 * t + 0.5 * a * t**2
        v = v0 + a * t

        self.figura.clear()
        ax1 = self.figura.add_subplot(211)
        ax2 = self.figura.add_subplot(212, sharex=ax1)
        ax1.plot(t, x, color="#176b87", linewidth=2)
        ax1.axhline(0, color="black", linewidth=0.6)
        ax1.set_ylabel("Posicao x (m)")
        ax1.set_title("Plano inclinado com atrito e tracao")
        ax1.grid(alpha=0.25)

        ax2.plot(t, v, color="#e76f51", linewidth=2)
        ax2.axhline(0, color="black", linewidth=0.6)
        ax2.set_xlabel("Tempo (s)")
        ax2.set_ylabel("Velocidade (m/s)")
        ax2.grid(alpha=0.25)
        self.figura.tight_layout(pad=2.0)

        mu_crit = abs(f_motriz) / normal if normal > 0 else np.inf
        self.rotulo_resultados.config(
            text=(
                f"Estado: {estado}\n"
                f"a = {a:.3f} m/s2\n"
                f"T = {tracao:.3f} N\n"
                f"N = {normal:.3f} N\n"
                f"mu critico = {mu_crit:.3f}"
            )
        )

    def _plotar_centripeta(self):
        m = self.parametros["m"].get()
        R = self.parametros["R"].get()
        v = self.parametros["v"].get()
        tf = self.parametros["tempo"].get()
        t = np.linspace(0.0, tf, 480)

        # MCU: omega = v/R e parametrizacao da circunferencia.
        omega = v / R
        x = R * np.cos(omega * t)
        y = R * np.sin(omega * t)
        # Pela 2a Lei na direcao radial: Fc = m*ac = m*v^2/R.
        fc = m * v**2 / R
        periodo = 2.0 * np.pi / omega

        self.figura.clear()
        ax1 = self.figura.add_subplot(121)
        ax2 = self.figura.add_subplot(122)

        ax1.plot(x, y, color="#176b87", linewidth=2)
        ax1.scatter([x[-1]], [y[-1]], s=80, color="#e76f51", zorder=3, label="Posicao final")
        ax1.plot([0, x[-1]], [0, y[-1]], "--", color="#555555", linewidth=1)
        ax1.set_aspect("equal", adjustable="box")
        margem = 1.18 * R
        ax1.set_xlim(-margem, margem)
        ax1.set_ylim(-margem, margem)
        ax1.set_xlabel("x (m)")
        ax1.set_ylabel("y (m)")
        ax1.set_title("Trajetoria circular")
        ax1.grid(alpha=0.25)
        ax1.legend(loc="upper right")

        ax2.plot(t, x, label="x(t)", color="#176b87")
        ax2.plot(t, y, label="y(t)", color="#e76f51")
        ax2.set_xlabel("Tempo (s)")
        ax2.set_ylabel("Posicao (m)")
        ax2.set_title("Componentes da posicao")
        ax2.grid(alpha=0.25)
        ax2.legend()
        self.figura.suptitle("Forca centripeta e Movimento Circular Uniforme")
        self.figura.tight_layout(pad=2.2)

        self.rotulo_resultados.config(
            text=(
                f"Fc = {fc:.3f} N\n"
                f"omega = {omega:.3f} rad/s\n"
                f"Periodo = {periodo:.3f} s\n"
                f"ac = {v**2 / R:.3f} m/s2"
            )
        )

    def _plotar_arrasto(self):
        m = self.parametros["m"].get()
        coef = self.parametros["coef"].get()
        tf = self.parametros["tempo"].get()
        t = np.linspace(0.0, tf, 420)
        modo = self.modo_arrasto.get()

        if modo == "Linear":
            # Arrasto linear: Fd = -b*v. Solucao fechada para queda a partir do repouso.
            vt = m * G / coef
            tau = m / coef
            v = vt * (1.0 - np.exp(-t / tau))
            y = vt * t - vt * tau * (1.0 - np.exp(-t / tau))
            t95 = -tau * np.log(0.05)
            unidade = "b em kg/s"
        else:
            # Arrasto quadratico: Fd = -c*v*|v|. Solucao fechada.
            vt = np.sqrt(m * G / coef)
            argumento = G * t / vt
            v = vt * np.tanh(argumento)
            # log(cosh(z)) pode transbordar para z muito grande. Aqui o intervalo
            # dos sliders o mantem seguro, mas logaddexp deixa a formula robusta.
            log_cosh = np.logaddexp(argumento, -argumento) - np.log(2.0)
            y = (vt**2 / G) * log_cosh
            t95 = (vt / G) * np.arctanh(0.95)
            unidade = "c em kg/m"

        v_livre = G * t
        y_livre = 0.5 * G * t**2

        self.figura.clear()
        ax1 = self.figura.add_subplot(211)
        ax2 = self.figura.add_subplot(212, sharex=ax1)
        ax1.plot(t, v, label=f"Com arrasto {modo.lower()}", color="#176b87", linewidth=2)
        ax1.plot(t, v_livre, "--", label="Sem arrasto: v = gt", color="#e76f51")
        ax1.axhline(vt, color="#2a9d8f", linestyle=":", label="Velocidade terminal")
        ax1.set_ylabel("Velocidade (m/s)")
        ax1.set_title("Queda vertical com e sem resistencia do ar")
        ax1.grid(alpha=0.25)
        ax1.legend()

        ax2.plot(t, y, label="Com arrasto", color="#176b87", linewidth=2)
        ax2.plot(t, y_livre, "--", label="Queda livre", color="#e76f51")
        ax2.set_xlabel("Tempo (s)")
        ax2.set_ylabel("Deslocamento y (m)")
        ax2.grid(alpha=0.25)
        ax2.legend()
        self.figura.tight_layout(pad=2.0)

        self.rotulo_resultados.config(
            text=(
                f"Modelo: {modo}\n"
                f"v_terminal = {vt:.3f} m/s\n"
                f"t(95% vt) = {t95:.3f} s\n"
                f"Coeficiente: {unidade}"
            )
        )


def main():
    raiz = tk.Tk()
    try:
        ttk.Style().theme_use("clam")
    except tk.TclError:
        pass
    SimuladorFisica(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()