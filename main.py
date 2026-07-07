"""
main.py
Entry point do DocStamp Pro.
Inicializa o banco de dados e exibe a tela de login.
"""

import sys
import os

# Garante que o diretório raiz do projeto esteja no PATH
sys.path.insert(0, os.path.dirname(__file__))

import customtkinter as ctk
from database import db
from ui.login_window import LoginWindow
from ui.main_window import MainWindow


def on_login_success(user: dict):
    """Callback chamado após login bem-sucedido."""
    app = MainWindow(user)

    # Se for admin, adiciona botão de gerenciar usuários na barra superior
    if user.get("role") == "admin":
        _add_admin_button(app, user)

    app.mainloop()


def _add_admin_button(app: MainWindow, user: dict):
    """Adiciona botão 'Gerenciar Usuários' para admins."""
    # Encontra a barra superior e adiciona o botão
    from ui.admin_window import AdminWindow

    def open_admin():
        AdminWindow(app)

    # Injeta botão na topbar (último grid row=0 da barra)
    for widget in app.winfo_children():
        if isinstance(widget, ctk.CTkFrame) and widget.winfo_height() == 60:
            ctk.CTkButton(
                widget,
                text="👥 Gerenciar",
                width=120, height=30,
                font=ctk.CTkFont(size=12),
                fg_color="#1D4ED8",
                hover_color="#1E40AF",
                text_color="#FFFFFF",
                corner_radius=8,
                command=open_admin,
            ).grid(row=0, column=3, padx=(0, 100), sticky="e")
            break


def start_app():
    """Inicializa e exibe a janela de login."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    login = LoginWindow(on_login_success=on_login_success)
    login.mainloop()


if __name__ == "__main__":
    # Inicializa banco de dados
    db.init_db()
    # Inicia o aplicativo
    start_app()
