"""
ui/login_window.py
Tela de Login do DocStamp Pro.
Layout inspirado no design Figma: split-screen azul escuro + formulário branco.
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import db
from utils.helpers import validate_email, center_window_on_cursor_monitor


# ── Paleta de cores ──────────────────────────────────────────────────────────
NAVY       = "#0F172A"
NAVY_MID   = "#1E293B"
BLUE_MAIN  = "#2563EB"
BLUE_HOVER = "#1D4ED8"
WHITE      = "#FFFFFF"
GRAY_100   = "#F1F5F9"
GRAY_400   = "#94A3B8"
GRAY_600   = "#475569"
RED_ERR    = "#EF4444"


class LoginWindow(ctk.CTk):
    """Janela principal de login."""

    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success

        self.title("DocStamp Pro — Login")
        self.geometry("960x600")
        self.resizable(False, False)
        self._configure_theme()
        self._build_ui()
        self._center_window()

        # Força janela ao primeiro plano
        self.deiconify()
        self.lift()
        self.focus_force()
        self.attributes("-topmost", True)
        self.after(500, lambda: self.attributes("-topmost", False))

        # Verifica sessão salva
        self._check_saved_session()

    def _configure_theme(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=NAVY)

    def _center_window(self):
        center_window_on_cursor_monitor(self, 960, 600)

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Painel Esquerdo (azul escuro) ─────────────────────────────────
        left = ctk.CTkFrame(self, fg_color=NAVY_MID, corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew")
        left.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        # Logo / ícone
        logo_frame = ctk.CTkFrame(left, fg_color="#2563EB", width=72, height=72,
                                   corner_radius=16)
        logo_frame.grid(row=1, column=0, padx=60, pady=(0, 20))
        logo_frame.grid_propagate(False)
        ctk.CTkLabel(
            logo_frame,
            text="📄",
            font=ctk.CTkFont(size=34),
            text_color=WHITE,
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Nome do app
        ctk.CTkLabel(
            left,
            text="DocStamp Pro",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=WHITE,
        ).grid(row=2, column=0, padx=60)

        ctk.CTkLabel(
            left,
            text="Sistema profissional de\ncarimbo de data em documentos.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=GRAY_400,
            justify="center",
        ).grid(row=3, column=0, padx=60, pady=(8, 0))

        # Rodapé esquerdo
        ctk.CTkLabel(
            left,
            text="© 2025 DocStamp Pro  ·  v1.0.0",
            font=ctk.CTkFont(size=11),
            text_color=GRAY_600,
        ).grid(row=4, column=0, padx=60, pady=(0, 30))

        # ── Painel Direito (formulário) ───────────────────────────────────
        right = ctk.CTkFrame(self, fg_color="#1C2333", corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(0, weight=1)
        right.grid_columnconfigure(0, weight=1)

        # Caixa central do formulário
        form_box = ctk.CTkFrame(right, fg_color="#263044", corner_radius=16,
                                 width=380)
        form_box.grid(row=0, column=0, padx=50, pady=60, sticky="nsew")
        form_box.grid_columnconfigure(0, weight=1)

        # Título do formulário
        ctk.CTkLabel(
            form_box,
            text="Entrar",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=WHITE,
        ).grid(row=0, column=0, padx=32, pady=(32, 4), sticky="w")

        ctk.CTkLabel(
            form_box,
            text="Acesse com suas credenciais corporativas",
            font=ctk.CTkFont(size=12),
            text_color=GRAY_400,
        ).grid(row=1, column=0, padx=32, pady=(0, 24), sticky="w")

        # Campo E-mail
        ctk.CTkLabel(
            form_box, text="E-MAIL CORPORATIVO",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=GRAY_400,
        ).grid(row=2, column=0, padx=32, sticky="w")

        self.email_entry = ctk.CTkEntry(
            form_box,
            placeholder_text="exemplo@empresa.com.br",
            height=44,
            font=ctk.CTkFont(size=13),
            fg_color="#1E293B",
            border_color="#334155",
            text_color=WHITE,
            placeholder_text_color=GRAY_400,
        )
        self.email_entry.grid(row=3, column=0, padx=32, pady=(6, 16), sticky="ew")

        # Campo Senha
        ctk.CTkLabel(
            form_box, text="SENHA",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=GRAY_400,
        ).grid(row=4, column=0, padx=32, sticky="w")

        self.password_entry = ctk.CTkEntry(
            form_box,
            placeholder_text="••••••••",
            show="•",
            height=44,
            font=ctk.CTkFont(size=13),
            fg_color="#1E293B",
            border_color="#334155",
            text_color=WHITE,
            placeholder_text_color=GRAY_400,
        )
        self.password_entry.grid(row=5, column=0, padx=32, pady=(6, 4), sticky="ew")

        # Toggle de visibilidade da senha
        self._pwd_visible = False
        self.toggle_btn = ctk.CTkButton(
            form_box,
            text="👁 Mostrar",
            width=90,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            text_color=GRAY_400,
            hover_color="#334155",
            command=self._toggle_password,
        )
        self.toggle_btn.grid(row=6, column=0, padx=32, pady=(0, 8), sticky="e")

        # Checkbox "Lembrar neste dispositivo"
        self.remember_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            form_box,
            text="Lembrar acesso neste dispositivo",
            variable=self.remember_var,
            font=ctk.CTkFont(size=12),
            text_color=GRAY_400,
            fg_color=BLUE_MAIN,
            hover_color=BLUE_HOVER,
            border_color="#475569",
        ).grid(row=7, column=0, padx=32, pady=(0, 20), sticky="w")

        # Mensagem de erro
        self.error_label = ctk.CTkLabel(
            form_box, text="",
            font=ctk.CTkFont(size=12),
            text_color=RED_ERR,
        )
        self.error_label.grid(row=8, column=0, padx=32, pady=(0, 4))

        # Botão Entrar
        self.login_btn = ctk.CTkButton(
            form_box,
            text="Entrar  →",
            height=48,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=BLUE_MAIN,
            hover_color=BLUE_HOVER,
            corner_radius=10,
            command=self._do_login,
        )
        self.login_btn.grid(row=9, column=0, padx=32, pady=(0, 32), sticky="ew")

        # Bind Enter key
        self.bind("<Return>", lambda e: self._do_login())
        self.email_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self._do_login())

    # ── Ações ─────────────────────────────────────────────────────────────────

    def _toggle_password(self):
        self._pwd_visible = not self._pwd_visible
        self.password_entry.configure(show="" if self._pwd_visible else "•")
        self.toggle_btn.configure(
            text="🙈 Ocultar" if self._pwd_visible else "👁 Mostrar"
        )

    def _show_error(self, msg: str):
        self.error_label.configure(text=msg)

    def _clear_error(self):
        self.error_label.configure(text="")

    def _do_login(self):
        self._clear_error()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        # Validações básicas
        if not email:
            self._show_error("⚠ Informe o e-mail.")
            return
        if not validate_email(email):
            self._show_error("⚠ E-mail inválido.")
            return
        if not password:
            self._show_error("⚠ Informe a senha.")
            return

        # Autenticação
        self.login_btn.configure(text="Verificando...", state="disabled")
        self.after(100, lambda: self._authenticate(email, password))

    def _authenticate(self, email: str, password: str):
        user = db.authenticate(email, password)
        self.login_btn.configure(text="Entrar  →", state="normal")

        if user is None:
            self._show_error("⚠ E-mail ou senha incorretos.")
            return

        # Salvar sessão se solicitado
        if self.remember_var.get():
            db.save_session(user["id"])

        self.destroy()
        self.on_login_success(user)

    def _check_saved_session(self):
        """Verifica se existe sessão salva e faz login automático."""
        user_id = db.load_session()
        if user_id:
            user = db.get_user_by_id(user_id)
            if user:
                self.destroy()
                self.on_login_success(user)
