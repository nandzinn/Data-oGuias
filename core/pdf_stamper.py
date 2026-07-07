"""
core/pdf_stamper.py
Lógica de carimbo de data em PDFs usando PyMuPDF (fitz).
Adiciona texto de data em qualquer canto (top-left, top-right, bottom-left, bottom-right) de cada página do PDF.
"""

import fitz  # PyMuPDF
import os
from datetime import datetime
from typing import List, Tuple


def hex_to_rgb_float(hex_color: str) -> Tuple[float, float, float]:
    """Converte cor hexadecimal para tupla RGB normalizada (0.0–1.0)."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return (r, g, b)


def _estimate_text_width(text: str, font_size: int) -> float:
    """
    Estima a largura do texto em pontos para a fonte Helvetica.
    Fator aproximado: 0.52 × font_size por caractere (média Helvetica).
    """
    return len(text) * font_size * 0.52


def stamp_pdf(
    input_path: str,
    output_path: str,
    date_str: str,
    color_hex: str = "#FF6B00",
    font_size: int = 14,
    position: str = "top-right",
    margin_x: float = 40,
    margin_y: float = 30,
) -> bool:
    """
    Adiciona um carimbo de data em todas as páginas de um PDF.

    Args:
        input_path:  Caminho do PDF original.
        output_path: Caminho de saída do PDF carimbado.
        date_str:    Texto da data (ex: "06/07/2025").
        color_hex:   Cor do texto em hex (ex: "#FF6B00").
        font_size:   Tamanho da fonte em pontos.
        position:    Posição do carimbo. Valores aceitos:
                     "top-right" (padrão), "top-left",
                     "bottom-right", "bottom-left".
                     Também aceita "top" (= top-left) e "bottom" (= bottom-left)
                     para retrocompatibilidade.
        margin_x:    Margem horizontal em pontos.
        margin_y:    Margem vertical em pontos.

    Returns:
        True em sucesso, False em falha.
    """
    # Normaliza valores legados
    if position == "top":
        position = "top-left"
    elif position == "bottom":
        position = "bottom-left"

    try:
        doc = fitz.open(input_path)
        color = hex_to_rgb_float(color_hex)

        for page in doc:
            page_rect = page.rect
            page_width = page_rect.width
            page_height = page_rect.height

            # ── Posição vertical ─────────────────────────────────────────────
            if position.startswith("top"):
                y = margin_y
            else:  # bottom-*
                y = page_height - margin_y

            # ── Posição horizontal ────────────────────────────────────────────
            if position.endswith("right"):
                text_width = _estimate_text_width(date_str, font_size)
                x = page_width - text_width - margin_x
                x = max(x, margin_x)  # garante que não saia da margem esquerda
            else:  # left
                x = margin_x

            # ── Insere o texto com PyMuPDF ────────────────────────────────────
            page.insert_text(
                point=fitz.Point(x, y),
                text=date_str,
                fontsize=font_size,
                color=color,
                fontname="helv",    # Helvetica (embutida no PyMuPDF)
                overlay=True,
            )

        # Cria pasta de saída se necessário
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc.save(output_path)
        doc.close()
        return True

    except Exception as e:
        print(f"[DocStamp] Erro ao carimbar {input_path}: {e}")
        return False


def stamp_folder(
    folder_path: str,
    date_str: str,
    color_hex: str = "#FF6B00",
    font_size: int = 14,
    position: str = "top",
    progress_callback=None,
) -> List[dict]:
    """
    Carimba todos os PDFs dentro de uma pasta.
    Os arquivos carimbados são salvos em subpasta '_carimbados'.

    Args:
        folder_path:       Caminho da pasta com os PDFs.
        date_str:          Data a ser carimbada.
        color_hex:         Cor do carimbo.
        font_size:         Tamanho da fonte.
        position:          "top" ou "bottom".
        progress_callback: Função chamada a cada arquivo (file_name, success).

    Returns:
        Lista de dicts com resultado de cada arquivo:
        [{"file": "nome.pdf", "output": "caminho", "success": True/False}]
    """
    output_dir = os.path.join(folder_path, "_carimbados")
    os.makedirs(output_dir, exist_ok=True)

    results = []
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".pdf")]

    for file_name in pdf_files:
        input_path = os.path.join(folder_path, file_name)
        output_path = os.path.join(output_dir, file_name)

        success = stamp_pdf(
            input_path=input_path,
            output_path=output_path,
            date_str=date_str,
            color_hex=color_hex,
            font_size=font_size,
            position=position,
        )

        result = {
            "file": file_name,
            "input": input_path,
            "output": output_path,
            "success": success,
        }
        results.append(result)

        if progress_callback:
            progress_callback(file_name, success)

    return results


def stamp_files(
    file_paths: List[str],
    date_str: str,
    color_hex: str = "#FF6B00",
    font_size: int = 14,
    position: str = "top",
    progress_callback=None,
) -> List[dict]:
    """
    Carimba uma lista de arquivos PDF individuais.
    Cada arquivo é salvo em subpasta '_carimbados' junto ao original.

    Args:
        file_paths:        Lista de caminhos completos dos PDFs.
        date_str:          Data a ser carimbada.
        color_hex:         Cor do carimbo.
        font_size:         Tamanho da fonte.
        position:          "top" ou "bottom".
        progress_callback: Função chamada a cada arquivo (file_name, success).

    Returns:
        Lista de resultados por arquivo.
    """
    results = []

    for input_path in file_paths:
        if not input_path.lower().endswith(".pdf"):
            continue

        folder = os.path.dirname(input_path)
        file_name = os.path.basename(input_path)
        output_dir = os.path.join(folder, "_carimbados")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, file_name)

        success = stamp_pdf(
            input_path=input_path,
            output_path=output_path,
            date_str=date_str,
            color_hex=color_hex,
            font_size=font_size,
            position=position,
        )

        result = {
            "file": file_name,
            "input": input_path,
            "output": output_path,
            "success": success,
        }
        results.append(result)

        if progress_callback:
            progress_callback(file_name, success)

    return results


def get_output_folder(file_path: str) -> str:
    """Retorna o caminho da pasta _carimbados para um arquivo."""
    folder = os.path.dirname(file_path)
    return os.path.join(folder, "_carimbados")
