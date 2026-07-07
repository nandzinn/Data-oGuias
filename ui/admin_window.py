"""
ui/admin_window.py
Painel de administração para gerenciar usuários do DocStamp Pro.
Acessível apenas para usuários com role = 'admin'.
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import db
from utils.helpers import validate_email, validate_password, PRESET_COLORS

# ── Paleta ───────────────────────────────────────────────────────────────────
NAVY       = "#0F172A"
NAVY_MID   = "#1E293B"
CARD       = "#1C2333"
CARD_LIGHT = "#263044"
BLUE_MAIN  = "#2563EB"
BLUE_HOVER = "#1D4ED8"
RED_ERR    = "#EF4444"
WHITE      = "#FFFFFF"
GRAY_400   = "#94A3B8"
GRAY_300   = "#CBD5E1"
BORDER     = "#334155"
GREEN      = "#16A34A"


class AdminWindow(ctk.CTkToplevel):
    """Janela de gerenciamento de usuários (apenas admin)."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("DocStamp Pro — Gerenciar Usuários")
        self.geometry("900x600")
        self.configure(fg_color=NAVY)
        self.lift()
        self.grab_set()
        self._build()
        self._center()
        self._load_users()

    def _center(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - 900) // 2
        y = (sh - 600) // 2
        self.geometry(f"900x600+{x}+{y}")

    def _build(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)

        # ── Cabeçalho ─────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=NAVY_MID, height=60, corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="👥  Gerenciar Funcionários",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=WHITE,
        ).grid(row=0, column=0, padx=24, sticky="w")

        # ── Lista de Usuários ─────────────────────────────────────────────
        list_panel = ctk.CTkFrame(self, fg_color=CARD, corner_radius=0)
        list_panel.grid(row=1, column=0, sticky="nsew")
        list_panel.grid_rowconfigure(1, weight=1)
        list_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            list_panel, text="Funcionários Cadastrados",
            font=ctk.CTkFont(size=15, weight="bold"), text_color=WHITE,
        ).grid(row=0, column=0, padx=20, pady=(16, 8), sticky="w")

        self.users_scroll = ctk.CTkScrollableFrame(
            list_panel, fg_color="transparent"
        )
        self.users_scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.users_scroll.grid_columnconfigure(0, weight=1)

        # ── Formulário Novo Usuário ───────────────────────────────────────
        form_panel = ctk.CTkFrame(self, fg_color=CARD_LIGHT, corner_radius=0)
        form_panel.grid(row=1, column=1, sticky="nsew")
        form_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            form_panel, text="Novo Funcionário",
            font=ctk.CTkFont(size=15, weight="bold"), text_color=WHITE,
        ).grid(row=0, column=0, padx=20, pady=(20, 4), sticky="w")

        ctk.CTkLabel(form_panel, text="Nome Completo",
                     font=ctk.CTkFont(size=11), text_color=GRAY_400,
        ).grid(row=1, column=0, padx=20, pady=(12, 4), sticky="w")

        self.name_entry = ctk.CTkEntry(
            form_panel, placeholder_text="Ex: Fernando Silva",
            height=40, fg_color=CARD, border_color=BORDER,
            text_color=WHITE, placeholder_text_color=GRAY_400,
        )
        self.name_entry.grid(row=2, column=0, padx=20, sticky="ew")

        ctk.CTkLabel(form_panel, text="E-mail Corporativo",
                     font=ctk.CTkFont(size=11), text_color=GRAY_400,
        ).grid(row=3, column=0, padx=20, pady=(12, 4), sticky="w")

        self.email_entry = ctk.CTkEntry(
            form_panel, placeholder_text="fernando@empresa.com.br",
            height=40, fg_color=CARD, border_color=BORDER,
            text_color=WHITE, placeholder_text_color=GRAY_400,
        )
        self.email_entry.grid(row=4, column=0, padx=20, sticky="ew")

        ctk.CTkLabel(form_panel, text="Senha Inicial",
                     font=ctk.CTkFont(size=11), text_color=GRAY_400,
        ).grid(row=5, column=0, padx=20, pady=(12, 4), sticky="w")

        self.password_entry = ctk.CTkEntry(
            form_panel, placeholder_text="Mínimo 8 caracteres",
            show="•", height=40,
            fg_color=CARD, border_color=BORDER,
            text_color=WHITE, placeholder_text_color=GRAY_400,
        )
        self.password_entry.grid(row=6, column=0, padx=20, sticky="ew")

        ctk.CTkLabel(form_panel, text="Cor do Carimbo",
                     font=ctk.CTkFont(size=11), text_color=GRAY_400,
        ).grid(row=7, column=0, padx=20, pady=(12, 4), sticky="w")

        # Paleta de cores
        self.color_var = ctk.StringVar(value="#F97316")
        colors_grid = ctk.CTkFrame(form_panel, fg_color="transparent")
        colors_grid.grid(row=8, column=0, padx=20, sticky="w")
        self.color_btns = {}

        for i, c in enumerate(PRESET_COLORS):
            btn = ctk.CTkButton(
                colors_grid, text="✓" if c["hex"] == self.color_var.get() else "",
                width=32, height=32, corner_radius=16,
                fg_color=c["hex"], hover_color=c["hex"],
                border_width=3 if c["hex"] == self.color_var.get() else 0,
                border_color=WHITE,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=WHITE,
                command=lambda h=c["hex"]: self._pick_color(h),
            )
            btn.grid(row=i // 5, column=i % 5, padx=3, pady=3)
            self.color_btns[c["hex"]] = btn

        ctk.CTkLabel(form_panel, text="Função",
                     font=ctk.CTkFont(size=11), text_color=GRAY_400,
        ).grid(row=9, column=0, padx=20, pady=(12, 4), sticky="w")

        self.role_var = ctk.StringVar(value="user")
        ctk.CTkSegmentedButton(
            form_panel, values=["Funcionário", "Admin"],
            variable=ctk.StringVar(value="Funcionário"),
            font=ctk.CTkFont(size=12),
            fg_color=CARD, selected_color=BLUE_MAIN,
            command=lambda v: self.role_var.set("user" if v == "Funcionário" else "admin"),
        ).grid(row=10, column=0, padx=20, pady=(0, 4), sticky="ew")

        self.form_error = ctk.CTkLabel(
            form_panel, text="",
            font=ctk.CTkFont(size=11), text_color=RED_ERR,
        )
        self.form_error.grid(row=11, column=0, padx=20, pady=(8, 0))

        ctk.CTkButton(
            form_panel, text="➕  Cadastrar",
            height=44,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=GREEN, hover_color="#15803D",
            corner_radius=10,
            command=self._create_user,
        ).grid(row=12, column=0, padx=20, pady=16, sticky="ew")

    def _pick_color(self, hex_color):
        self.color_var.set(hex_color)
        for h, btn in self.color_btns.items():
            is_sel = h == hex_color
            btn.configure(text="✓" if is_sel else "", border_width=3 if is_sel else 0)

    def _load_users(self):
        """Carrega e exibe a lista de usuários."""
        for w in self.users_scroll.winfo_children():
            w.destroy()

        users = db.get_all_users()
        if not users:
            ctk.CTkLabel(
                self.users_scroll, text="Nenhum usuário cadastrado.",
                font=ctk.CTkFont(size=13), text_color=GRAY_400,
            ).pack(pady=40)
            return

        for u in users:
            self._user_row(u)

    def _user_row(self, user: dict):
        row = ctk.CTkFrame(self.users_scroll, fg_color=CARD_LIGHT, corner_radius=8, height=52)
        row.pack(fill="x", pady=4)
        row.pack_propagate(False)
        row.grid_columnconfigure(2, weight=1)

        # Avatar com cor do carimbo
        av = ctk.CTkFrame(row, fg_color=user.get("stamp_color", BLUE_MAIN),
                           width=34, height=34, corner_radius=17)
        av.grid(row=0, column=0, padx=(12, 10), pady=9)
        av.grid_propagate(False)
        initials = "".join(p[0].upper() for p in user["name"].split()[:2])
        ctk.CTkLabel(av, text=initials, font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=WHITE).place(relx=0.5, rely=0.5, anchor="center")

        # Nome + e-mail
        info = ctk.CTkFrame(row, fg_color="transparent")
        info.grid(row=0, column=1, columnspan=2, sticky="ew")

        ctk.CTkLabel(info, text=user["name"],
                     font=ctk.CTkFont(size=13, weight="bold"), text_color=WHITE,
                     anchor="w").pack(anchor="w")
        ctk.CTkLabel(info, text=user["email"],
                     font=ctk.CTkFont(size=11), text_color=GRAY_400,
                     anchor="w").pack(anchor="w")

        # Role badge
        role_color = "#1D4ED8" if user["role"] == "admin" else GRAY_400
        role_text  = "Admin" if user["role"] == "admin" else "Usuário"
        ctk.CTkLabel(
            row, text=role_text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=role_color,
            fg_color=CARD, corner_radius=6, padx=8, pady=3,
        ).grid(row=0, column=3, padx=(0, 8))

        # Botão excluir
        if user["role"] != "admin":
            ctk.CTkButton(
                row, text="🗑",
                width=32, height=32,
                font=ctk.CTkFont(size=14),
                fg_color="transparent", hover_color="#7F1D1D",
                text_color=RED_ERR,
                command=lambda uid=user["id"], name=user["name"]: self._delete_user(uid, name),
            ).grid(row=0, column=4, padx=(0, 12))

    def _create_user(self):
        self.form_error.configure(text="")
        name     = self.name_entry.get().strip()
        email    = self.email_entry.get().strip()
        password = self.password_entry.get()
        color    = self.color_var.get()
        role     = self.role_var.get()

        if not name:
            self.form_error.configure(text="⚠ Informe o nome.")
            return
        if not validate_email(email):
            self.form_error.configure(text="⚠ E-mail inválido.")
            return
        valid, msg = validate_password(password)
        if not valid:
            self.form_error.configure(text=f"⚠ {msg}")
            return

        success = db.create_user(name, email, password, role=role, stamp_color=color)
        if not success:
            self.form_error.configure(text="⚠ E-mail já cadastrado.")
            return

        # Limpa formulário
        self.name_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.password_entry.delete(0, "end")

        messagebox.showinfo("Sucesso", f"Funcionário '{name}' cadastrado com sucesso!")
        self._load_users()

    def _delete_user(self, user_id: int, name: str):
        if messagebox.askyesno("Confirmar", f"Remover o usuário '{name}'?"):
            db.delete_user(user_id)
            self._load_users()
