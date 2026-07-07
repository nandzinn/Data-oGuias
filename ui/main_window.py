"""
ui/main_window.py
Janela principal do DocStamp Pro pós-login.
Contém: barra superior, painel de upload (esquerda), painel de configurações (direita).
"""

import customtkinter as ctk
import threading
import os
import sys
from tkinter import filedialog, messagebox

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import db
from core.pdf_stamper import stamp_files, stamp_folder, get_output_folder
from utils.helpers import format_date_br, PRESET_COLORS, truncate_filename, center_window_on_cursor_monitor
from datetime import datetime


# ── Paleta ───────────────────────────────────────────────────────────────────
NAVY       = "#0F172A"
NAVY_MID   = "#1E293B"
CARD       = "#1C2333"
CARD_LIGHT = "#263044"
BLUE_MAIN  = "#2563EB"
BLUE_HOVER = "#1D4ED8"
GREEN      = "#16A34A"
GREEN_LIGHT= "#22C55E"
RED_ERR    = "#EF4444"
WHITE      = "#FFFFFF"
GRAY_300   = "#CBD5E1"
GRAY_400   = "#94A3B8"
GRAY_600   = "#475569"
BORDER     = "#334155"


class MainWindow(ctk.CTk):
    """Janela principal do aplicativo após login."""

    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.selected_files: list[str] = []
        self.processing = False

        self.title(f"DocStamp Pro — {user['name']}")
        self.geometry("1200x720")
        self.minsize(900, 600)
        self._configure_theme()
        self._build_ui()
        self._center_window()

        # Força janela ao primeiro plano
        self.deiconify()
        self.lift()
        self.focus_force()
        self.attributes("-topmost", True)
        self.after(500, lambda: self.attributes("-topmost", False))

    def _configure_theme(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=NAVY)

    def _center_window(self):
        center_window_on_cursor_monitor(self, 1200, 720)

    # ── Construção da UI ──────────────────────────────────────────────────────

    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_topbar()
        self._build_content()

    def _build_topbar(self):
        """Barra superior com logo, nome do usuário e logout."""
        bar = ctk.CTkFrame(self, fg_color=NAVY_MID, height=60, corner_radius=0)
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_columnconfigure(1, weight=1)
        bar.grid_propagate(False)

        # Logo
        logo_frame = ctk.CTkFrame(bar, fg_color=BLUE_MAIN, width=36, height=36,
                                   corner_radius=8)
        logo_frame.grid(row=0, column=0, padx=20, pady=12)
        logo_frame.grid_propagate(False)
        ctk.CTkLabel(logo_frame, text="📄", font=ctk.CTkFont(size=18),
                     text_color=WHITE).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            bar, text="DocStamp Pro",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=WHITE,
        ).grid(row=0, column=1, padx=(8, 0), sticky="w")

        # Info do usuário
        user_info = ctk.CTkFrame(bar, fg_color="transparent")
        user_info.grid(row=0, column=2, padx=20, sticky="e")

        # Avatar circular com cor do usuário
        avatar = ctk.CTkFrame(user_info, fg_color=self.user.get("stamp_color", BLUE_MAIN),
                               width=34, height=34, corner_radius=17)
        avatar.grid(row=0, column=0, padx=(0, 10))
        avatar.grid_propagate(False)
        initials = "".join(p[0].upper() for p in self.user["name"].split()[:2])
        ctk.CTkLabel(avatar, text=initials, font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=WHITE).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            user_info, text=self.user["name"],
            font=ctk.CTkFont(size=13, weight="bold"), text_color=WHITE,
        ).grid(row=0, column=1)

        ctk.CTkButton(
            user_info, text="Sair",
            width=70, height=30,
            font=ctk.CTkFont(size=12),
            fg_color=CARD_LIGHT, hover_color="#334155",
            text_color=GRAY_400,
            command=self._logout,
        ).grid(row=0, column=2, padx=(16, 0))

    def _build_content(self):
        """Área principal: upload (esquerda) + config (direita)."""
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=24, pady=20)
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=2)

        # Painel esquerdo: upload
        self.left_panel = self._build_upload_panel(content)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        # Painel direito: configurações
        self.right_panel = self._build_config_panel(content)
        self.right_panel.grid(row=0, column=1, sticky="nsew")

    # ── Painel de Upload ──────────────────────────────────────────────────────

    def _build_upload_panel(self, parent) -> ctk.CTkFrame:
        panel = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=16)
        panel.grid_rowconfigure(2, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        # Título
        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(20, 0), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="Documentos",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=WHITE,
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Adicione PDFs individuais ou uma pasta inteira",
            font=ctk.CTkFont(size=12),
            text_color=GRAY_400,
        ).grid(row=1, column=0, sticky="w")

        # Botões de seleção
        btn_row = ctk.CTkFrame(panel, fg_color="transparent")
        btn_row.grid(row=1, column=0, padx=24, pady=12, sticky="ew")

        ctk.CTkButton(
            btn_row, text="+ PDF(s)",
            height=38, width=130,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=BLUE_MAIN, hover_color=BLUE_HOVER,
            corner_radius=8,
            command=self._select_files,
        ).grid(row=0, column=0, padx=(0, 10))

        ctk.CTkButton(
            btn_row, text="📁 Pasta Inteira",
            height=38, width=150,
            font=ctk.CTkFont(size=13),
            fg_color=CARD_LIGHT, hover_color="#334155",
            border_width=1, border_color=BORDER,
            text_color=WHITE,
            corner_radius=8,
            command=self._select_folder,
        ).grid(row=0, column=1)

        # Área de drop / lista de arquivos
        self.drop_frame = ctk.CTkFrame(panel, fg_color=CARD_LIGHT, corner_radius=12,
                                        border_width=2, border_color=BORDER)
        self.drop_frame.grid(row=2, column=0, padx=24, pady=(0, 16), sticky="nsew")
        self.drop_frame.grid_rowconfigure(0, weight=1)
        self.drop_frame.grid_columnconfigure(0, weight=1)

        # Placeholder (quando vazio)
        self.drop_placeholder = ctk.CTkFrame(self.drop_frame, fg_color="transparent")
        self.drop_placeholder.grid(row=0, column=0)

        ctk.CTkLabel(
            self.drop_placeholder, text="📂",
            font=ctk.CTkFont(size=48),
            text_color=GRAY_600,
        ).grid(row=0, column=0, pady=(40, 8))

        ctk.CTkLabel(
            self.drop_placeholder,
            text="Clique em '+ PDF(s)' ou '📁 Pasta Inteira'\npara selecionar seus documentos",
            font=ctk.CTkFont(size=13),
            text_color=GRAY_400, justify="center",
        ).grid(row=1, column=0, pady=(0, 40))

        # Lista scrollável de arquivos
        self.files_scroll = ctk.CTkScrollableFrame(
            self.drop_frame, fg_color="transparent", corner_radius=0
        )
        # Oculto inicialmente

        # Contador
        self.counter_label = ctk.CTkLabel(
            panel,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=GRAY_400,
        )
        self.counter_label.grid(row=3, column=0, padx=24, pady=(0, 20), sticky="w")

        return panel

    # ── Painel de Configurações ───────────────────────────────────────────────

    def _build_config_panel(self, parent) -> ctk.CTkFrame:
        panel = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=16)
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            panel, text="Configurações do Carimbo",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=WHITE,
        ).grid(row=0, column=0, padx=24, pady=(20, 4), sticky="w")

        ctk.CTkLabel(
            panel,
            text="Personalize a data, cor e tamanho",
            font=ctk.CTkFont(size=12), text_color=GRAY_400,
        ).grid(row=1, column=0, padx=24, pady=(0, 20), sticky="w")

        sep = ctk.CTkFrame(panel, fg_color=BORDER, height=1)
        sep.grid(row=2, column=0, padx=24, sticky="ew")

        # ── Data ─────────────────────────────────────────────────────────────
        ctk.CTkLabel(
            panel, text="DATA DO CARIMBO",
            font=ctk.CTkFont(size=10, weight="bold"), text_color=GRAY_400,
        ).grid(row=3, column=0, padx=24, pady=(20, 6), sticky="w")

        date_frame = ctk.CTkFrame(panel, fg_color="transparent")
        date_frame.grid(row=4, column=0, padx=24, sticky="ew")
        date_frame.grid_columnconfigure(0, weight=1)

        self.date_entry = ctk.CTkEntry(
            date_frame,
            placeholder_text="DD/MM/AAAA",
            height=42,
            font=ctk.CTkFont(size=14),
            fg_color=CARD_LIGHT, border_color=BORDER,
            text_color=WHITE, placeholder_text_color=GRAY_400,
        )
        self.date_entry.grid(row=0, column=0, sticky="ew")
        self.date_entry.insert(0, format_date_br())  # data de hoje

        ctk.CTkButton(
            date_frame, text="📅 Hoje",
            width=80, height=42,
            font=ctk.CTkFont(size=12),
            fg_color=CARD_LIGHT, hover_color="#334155",
            border_width=1, border_color=BORDER,
            text_color=WHITE, corner_radius=8,
            command=lambda: (self.date_entry.delete(0, "end"),
                             self.date_entry.insert(0, format_date_br())),
        ).grid(row=0, column=1, padx=(8, 0))

        # ── Cor ──────────────────────────────────────────────────────────────
        ctk.CTkLabel(
            panel, text="COR DO CARIMBO",
            font=ctk.CTkFont(size=10, weight="bold"), text_color=GRAY_400,
        ).grid(row=5, column=0, padx=24, pady=(20, 6), sticky="w")

        # Paleta de cores rápida
        colors_frame = ctk.CTkFrame(panel, fg_color="transparent")
        colors_frame.grid(row=6, column=0, padx=24, sticky="ew")

        self.selected_color = ctk.StringVar(
            value=self.user.get("stamp_color", "#F97316")
        )

        self.color_buttons = {}
        for i, color in enumerate(PRESET_COLORS):
            col = i % 5
            row = i // 5
            is_selected = color["hex"] == self.selected_color.get()
            btn = ctk.CTkButton(
                colors_frame,
                text="✓" if is_selected else "",
                width=42, height=42,
                corner_radius=21,
                fg_color=color["hex"],
                hover_color=color["hex"],
                border_width=3 if is_selected else 0,
                border_color=WHITE,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=WHITE,
                command=lambda h=color["hex"]: self._select_color(h),
            )
            btn.grid(row=row, column=col, padx=4, pady=4)
            self.color_buttons[color["hex"]] = btn

        # Campo de cor personalizada
        custom_frame = ctk.CTkFrame(panel, fg_color="transparent")
        custom_frame.grid(row=7, column=0, padx=24, pady=(8, 0), sticky="ew")
        custom_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            custom_frame, text="HEX:",
            font=ctk.CTkFont(size=12), text_color=GRAY_400,
        ).grid(row=0, column=0, padx=(0, 8))

        self.hex_entry = ctk.CTkEntry(
            custom_frame,
            textvariable=self.selected_color,
            width=120, height=36,
            font=ctk.CTkFont(size=13),
            fg_color=CARD_LIGHT, border_color=BORDER,
            text_color=WHITE,
        )
        self.hex_entry.grid(row=0, column=1, sticky="w")

        # Preview da cor
        self.color_preview = ctk.CTkFrame(
            custom_frame,
            fg_color=self.selected_color.get(),
            width=36, height=36, corner_radius=8,
        )
        self.color_preview.grid(row=0, column=2, padx=(8, 0))
        self.color_preview.grid_propagate(False)

        self.selected_color.trace_add("write", self._on_color_entry_change)

        # ── Tamanho da Fonte ─────────────────────────────────────────────────
        ctk.CTkLabel(
            panel, text="TAMANHO DA FONTE",
            font=ctk.CTkFont(size=10, weight="bold"), text_color=GRAY_400,
        ).grid(row=8, column=0, padx=24, pady=(20, 6), sticky="w")

        size_frame = ctk.CTkFrame(panel, fg_color="transparent")
        size_frame.grid(row=9, column=0, padx=24, sticky="ew")
        size_frame.grid_columnconfigure(0, weight=1)

        self.size_var = ctk.IntVar(value=self.user.get("stamp_size", 14))

        self.size_slider = ctk.CTkSlider(
            size_frame,
            from_=8, to=36,
            variable=self.size_var,
            height=20,
            button_color=BLUE_MAIN,
            button_hover_color=BLUE_HOVER,
            progress_color=BLUE_MAIN,
            command=lambda v: self.size_label.configure(text=f"{int(v)}pt"),
        )
        self.size_slider.grid(row=0, column=0, sticky="ew")

        self.size_label = ctk.CTkLabel(
            size_frame, text=f"{self.size_var.get()}pt",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=WHITE, width=50,
        )
        self.size_label.grid(row=0, column=1, padx=(12, 0))

        # ── Posição ───────────────────────────────────────────────────────────
        ctk.CTkLabel(
            panel, text="POSIÇÃO DO CARIMBO",
            font=ctk.CTkFont(size=10, weight="bold"), text_color=GRAY_400,
        ).grid(row=10, column=0, padx=24, pady=(20, 8), sticky="w")

        self.position_var = ctk.StringVar(
            value=self.user.get("stamp_position", "top-right")
        )

        pos_frame = ctk.CTkFrame(panel, fg_color="transparent")
        pos_frame.grid(row=11, column=0, padx=24, sticky="ew")
        pos_frame.grid_columnconfigure((0, 1), weight=1)

        # Mapa de posições: (valor_interno, label, linha, coluna)
        POS_OPTIONS = [
            ("top-left",     "↖  Superior Esq.", 0, 0),
            ("top-right",    "↗  Superior Dir.", 0, 1),
            ("bottom-left",  "↙  Inferior Esq.", 1, 0),
            ("bottom-right", "↘  Inferior Dir.", 1, 1),
        ]

        self._pos_buttons: dict[str, ctk.CTkButton] = {}
        current_pos = self.position_var.get()

        for value, label, grid_row, grid_col in POS_OPTIONS:
            is_selected = value == current_pos
            btn = ctk.CTkButton(
                pos_frame,
                text=label,
                height=36,
                font=ctk.CTkFont(size=12),
                fg_color=BLUE_MAIN if is_selected else CARD_LIGHT,
                hover_color=BLUE_HOVER,
                border_width=2 if is_selected else 1,
                border_color=BLUE_MAIN if is_selected else BORDER,
                text_color=WHITE,
                corner_radius=8,
                command=lambda v=value: self._select_position(v),
            )
            btn.grid(row=grid_row, column=grid_col,
                     padx=(0, 6) if grid_col == 0 else (6, 0),
                     pady=4, sticky="ew")
            self._pos_buttons[value] = btn

        # ── Separador + Botão ────────────────────────────────────────────────
        sep2 = ctk.CTkFrame(panel, fg_color=BORDER, height=1)
        sep2.grid(row=12, column=0, padx=24, pady=(24, 16), sticky="ew")

        # Barra de progresso
        self.progress_bar = ctk.CTkProgressBar(
            panel, height=6, fg_color=CARD_LIGHT,
            progress_color=GREEN, corner_radius=3,
        )
        self.progress_bar.set(0)
        self.progress_bar.grid(row=13, column=0, padx=24, pady=(0, 8), sticky="ew")
        self.progress_bar.grid_remove()

        self.status_label = ctk.CTkLabel(
            panel, text="",
            font=ctk.CTkFont(size=12), text_color=GRAY_400,
        )
        self.status_label.grid(row=14, column=0, padx=24, pady=(0, 8))

        self.stamp_btn = ctk.CTkButton(
            panel,
            text="▶  Carimbar PDFs",
            height=52,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=BLUE_MAIN, hover_color=BLUE_HOVER,
            corner_radius=10,
            command=self._start_stamping,
        )
        self.stamp_btn.grid(row=15, column=0, padx=24, pady=(0, 24), sticky="ew")

        return panel

    # ── Ações de Arquivos ─────────────────────────────────────────────────────

    def _select_files(self):
        paths = filedialog.askopenfilenames(
            title="Selecionar PDFs",
            filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")],
        )
        if paths:
            for p in paths:
                if p not in self.selected_files:
                    self.selected_files.append(p)
            self._refresh_file_list()

    def _select_folder(self):
        folder = filedialog.askdirectory(title="Selecionar pasta com PDFs")
        if folder:
            pdfs = [os.path.join(folder, f)
                    for f in os.listdir(folder)
                    if f.lower().endswith(".pdf")]
            added = 0
            for p in pdfs:
                if p not in self.selected_files:
                    self.selected_files.append(p)
                    added += 1
            if added == 0:
                messagebox.showinfo("Nenhum PDF encontrado",
                                    "Nenhum arquivo PDF foi encontrado na pasta selecionada.")
            else:
                self._refresh_file_list()

    def _remove_file(self, path: str):
        if path in self.selected_files:
            self.selected_files.remove(path)
        self._refresh_file_list()

    def _refresh_file_list(self):
        """Atualiza a lista de arquivos exibida."""
        # Limpa widgets anteriores
        for widget in self.files_scroll.winfo_children():
            widget.destroy()

        count = len(self.selected_files)

        if count == 0:
            self.files_scroll.grid_remove()
            self.drop_placeholder.grid(row=0, column=0)
            self.counter_label.configure(text="")
            return

        # Exibe lista
        self.drop_placeholder.grid_remove()
        self.files_scroll.grid(row=0, column=0, sticky="nsew",
                                padx=8, pady=8)

        for i, path in enumerate(self.selected_files):
            file_name = os.path.basename(path)
            row_frame = ctk.CTkFrame(self.files_scroll, fg_color=CARD, corner_radius=8,
                                      height=44)
            row_frame.pack(fill="x", pady=3)
            row_frame.pack_propagate(False)
            row_frame.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                row_frame, text="📄",
                font=ctk.CTkFont(size=16), text_color=BLUE_MAIN,
            ).grid(row=0, column=0, padx=(12, 8), sticky="w")

            ctk.CTkLabel(
                row_frame, text=truncate_filename(file_name, 35),
                font=ctk.CTkFont(size=12), text_color=GRAY_300,
                anchor="w",
            ).grid(row=0, column=1, sticky="ew")

            ctk.CTkButton(
                row_frame, text="✕",
                width=28, height=28,
                font=ctk.CTkFont(size=11),
                fg_color="transparent", hover_color=RED_ERR,
                text_color=GRAY_400, corner_radius=6,
                command=lambda p=path: self._remove_file(p),
            ).grid(row=0, column=2, padx=(0, 8))

        self.counter_label.configure(
            text=f"📋  {count} arquivo{'s' if count > 1 else ''} selecionado{'s' if count > 1 else ''}"
        )

    # ── Cor ──────────────────────────────────────────────────────────────────

    def _select_color(self, hex_color: str):
        self.selected_color.set(hex_color)
        for h, btn in self.color_buttons.items():
            is_sel = h == hex_color
            btn.configure(text="✓" if is_sel else "", border_width=3 if is_sel else 0)
        try:
            self.color_preview.configure(fg_color=hex_color)
        except Exception:
            pass

    def _on_color_entry_change(self, *args):
        hex_val = self.selected_color.get()
        if len(hex_val) == 7 and hex_val.startswith("#"):
            try:
                self.color_preview.configure(fg_color=hex_val)
            except Exception:
                pass

    def _select_position(self, value: str):
        """Atualiza a posição selecionada e o visual dos botões."""
        self.position_var.set(value)
        for pos, btn in self._pos_buttons.items():
            is_sel = pos == value
            btn.configure(
                fg_color=BLUE_MAIN if is_sel else CARD_LIGHT,
                border_width=2 if is_sel else 1,
                border_color=BLUE_MAIN if is_sel else BORDER,
            )

    # ── Processamento ─────────────────────────────────────────────────────────

    def _start_stamping(self):
        if self.processing:
            return

        if not self.selected_files:
            messagebox.showwarning("Nenhum arquivo", "Adicione pelo menos um PDF antes de continuar.")
            return

        date_str = self.date_entry.get().strip()
        if not date_str:
            messagebox.showwarning("Data inválida", "Informe a data do carimbo.")
            return

        color = self.selected_color.get()
        size = int(self.size_var.get())
        position = self.position_var.get()

        # Salva preferências do usuário
        db.update_user_preferences(self.user["id"], color, size, position)
        self.user["stamp_color"] = color
        self.user["stamp_size"] = size
        self.user["stamp_position"] = position

        self.processing = True
        self.stamp_btn.configure(text="⏳  Processando...", state="disabled")
        self.progress_bar.grid()
        self.progress_bar.set(0)
        self.status_label.configure(text=f"Carimbando 0 / {len(self.selected_files)} arquivos...")

        thread = threading.Thread(
            target=self._run_stamping,
            args=(list(self.selected_files), date_str, color, size, position),
            daemon=True,
        )
        thread.start()

    def _run_stamping(self, files, date_str, color, size, position):
        """Executa o carimbo em thread separada para não travar a UI."""
        total = len(files)
        results = []
        processed = 0

        def on_progress(file_name, success):
            nonlocal processed
            processed += 1
            pct = processed / total
            self.after(0, lambda: self.progress_bar.set(pct))
            self.after(0, lambda: self.status_label.configure(
                text=f"Carimbando {processed} / {total} arquivos..."
            ))

        results = stamp_files(
            file_paths=files,
            date_str=date_str,
            color_hex=color,
            font_size=size,
            position=position,
            progress_callback=on_progress,
        )

        # Registra logs de auditoria (LGPD)
        for r in results:
            if r["success"]:
                db.log_stamp(
                    user_id=self.user["id"],
                    file_name=r["file"],
                    file_path=r["output"],
                    stamp_date=date_str,
                    stamp_color=color,
                    stamp_size=size,
                    stamp_position=position,
                )

        self.after(0, lambda: self._show_results(results))

    def _show_results(self, results: list):
        """Exibe a tela de resultados."""
        self.processing = False
        self.stamp_btn.configure(text="▶  Carimbar PDFs", state="normal")
        self.progress_bar.set(1.0)

        # Cria janela de resultados
        ResultsWindow(self, results, self.user)

        # Reset
        self.selected_files.clear()
        self._refresh_file_list()
        self.progress_bar.set(0)
        self.progress_bar.grid_remove()
        self.status_label.configure(text="")

    # ── Logout ────────────────────────────────────────────────────────────────

    def _logout(self):
        if messagebox.askyesno("Sair", "Deseja sair do DocStamp Pro?"):
            db.clear_session()
            self.destroy()
            import main as app_main
            app_main.start_app()


class ResultsWindow(ctk.CTkToplevel):
    """Janela pop-up com os resultados do processamento."""

    def __init__(self, parent, results: list, user: dict):
        super().__init__(parent)
        self.results = results
        self.user = user

        success = [r for r in results if r["success"]]
        failed  = [r for r in results if not r["success"]]

        self.title("DocStamp Pro — Resultados")
        self.geometry("600x520")
        self.resizable(False, False)
        self.configure(fg_color=NAVY)
        self.lift()
        self.grab_set()
        self._build(success, failed)
        self._center()

    def _center(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - 600) // 2
        y = (sh - 520) // 2
        self.geometry(f"600x520+{x}+{y}")

    def _build(self, success, failed):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color=NAVY_MID, corner_radius=0, height=80)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text=f"✅  {len(success)} PDF{'s' if len(success) != 1 else ''} carimbado{'s' if len(success) != 1 else ''} com sucesso!",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=GREEN_LIGHT,
        ).grid(row=0, column=0, pady=24)

        if failed:
            ctk.CTkLabel(
                header,
                text=f"⚠  {len(failed)} arquivo(s) com erro",
                font=ctk.CTkFont(size=13), text_color="#FBBF24",
            ).grid(row=1, column=0, pady=(0, 12))

        # Stats
        stats = ctk.CTkFrame(self, fg_color=CARD, corner_radius=0)
        stats.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        stats.grid_columnconfigure((0, 1), weight=1)

        self._stat_box(stats, "PROCESSADOS", str(len(self.results)), BLUE_MAIN, 0)
        self._stat_box(stats, "COM SUCESSO",  str(len(success)),      GREEN,     1)

        # Lista de resultados
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=16)

        for r in self.results:
            row_frame = ctk.CTkFrame(scroll, fg_color=CARD_LIGHT, corner_radius=8, height=50)
            row_frame.pack(fill="x", pady=4)
            row_frame.pack_propagate(False)
            row_frame.grid_columnconfigure(1, weight=1)

            icon = "✅" if r["success"] else "❌"
            color = GREEN_LIGHT if r["success"] else RED_ERR

            ctk.CTkLabel(row_frame, text=icon, font=ctk.CTkFont(size=18)).grid(
                row=0, column=0, padx=(14, 8))

            ctk.CTkLabel(
                row_frame, text=r["file"],
                font=ctk.CTkFont(size=13), text_color=WHITE, anchor="w",
            ).grid(row=0, column=1, sticky="ew")

            badge_txt = "Carimbado" if r["success"] else "Erro"
            badge = ctk.CTkLabel(
                row_frame, text=badge_txt,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=color,
                fg_color="#1A2B1A" if r["success"] else "#2B1A1A",
                corner_radius=6,
                padx=10, pady=4,
            )
            badge.grid(row=0, column=2, padx=(0, 14))

        # Botões
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=3, column=0, pady=(0, 20))

        if success:
            out_folder = os.path.dirname(success[0]["output"])
            ctk.CTkButton(
                btn_row, text="📂  Abrir Pasta",
                height=44, width=180,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=GREEN, hover_color="#15803D",
                corner_radius=10,
                command=lambda f=out_folder: os.startfile(f),
            ).grid(row=0, column=0, padx=8)

        ctk.CTkButton(
            btn_row, text="✕  Fechar",
            height=44, width=130,
            font=ctk.CTkFont(size=14),
            fg_color=CARD_LIGHT, hover_color="#334155",
            text_color=WHITE, corner_radius=10,
            command=self.destroy,
        ).grid(row=0, column=1, padx=8)

    def _stat_box(self, parent, label, value, color, col):
        box = ctk.CTkFrame(parent, fg_color=CARD_LIGHT, corner_radius=12)
        box.grid(row=0, column=col, padx=12, pady=16, sticky="ew")

        ctk.CTkLabel(box, text=value,
                     font=ctk.CTkFont(size=32, weight="bold"),
                     text_color=color).pack(pady=(16, 4))
        ctk.CTkLabel(box, text=label,
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=GRAY_400).pack(pady=(0, 16))
