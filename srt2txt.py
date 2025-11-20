#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
srt2txt.py — Conversor SRT → TXT
Copyright (c) 2025 Alexandre Ramos Fonseca
Licença: MIT (consulte o arquivo LICENSE para detalhes)

Permissão é concedida, gratuitamente, para qualquer pessoa obter uma cópia
deste software e dos arquivos de documentação associados (o "Software"),
para usar o Software sem restrições, incluindo, sem limitação, os direitos
de usar, copiar, modificar, mesclar, publicar, distribuir, sublicenciar
e/ou vender cópias do Software.
O Software é fornecido "como está", sem garantia de qualquer tipo.

English:
srt2txt.py — SRT → TXT Converter
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software.
The Software is provided "as is", without warranty of any kind.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from typing import List, Optional


# Padrão de timestamp típico de SRT (00:00:01,000 --> 00:00:03,000)
# Typical SRT timestamp pattern (00:00:01,000 --> 00:00:03,000)
TIMESTAMP_PATTERN = re.compile(
    r"\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}"
)


def _ler_arquivo_srt(caminho: Path) -> Optional[str]:
    """
    Lê um arquivo SRT tentando UTF-8 e, em caso de falha, Latin-1.
    Retorna o conteúdo como string ou None em caso de erro.

    English:
    Reads an SRT file, trying UTF-8 first and then Latin-1 if it fails.
    Returns the file content as a string, or None on error.
    """
    # Tenta dois encodings comuns: UTF-8 e Latin-1
    # Try two common encodings: UTF-8 and Latin-1
    for encoding in ("utf-8", "latin-1"):
        try:
            return caminho.read_text(encoding=encoding)
        except UnicodeDecodeError:
            # Se der erro de decodificação, tenta o próximo encoding
            # On decoding error, try the next encoding
            continue
        except FileNotFoundError:
            print(f"Erro: Arquivo '{caminho}' não encontrado.")
            # Error: file not found
            return None
        except OSError as e:
            print(f"Erro ao ler arquivo '{caminho}': {e}")
            # Generic OS error while reading
            return None

    print(f"Erro: não foi possível decodificar '{caminho}' como UTF-8 nem Latin-1.")
    # If both encodings fail, returns None
    return None


def _extrair_blocos_legenda(conteudo: str) -> List[List[str]]:
    """
    Divide o conteúdo do SRT em blocos de legenda.
    Cada bloco é retornado como uma lista de linhas (sem quebras de linha).

    English:
    Splits the SRT content into subtitle blocks.
    Each block is returned as a list of lines (without newline characters).
    """
    # Separa por linhas em branco (uma ou mais) para identificar blocos.
    # Split by one or more blank lines to identify subtitle blocks.
    blocos_brutos = re.split(r"\n\s*\n", conteudo.strip(), flags=re.MULTILINE)
    blocos_processados: List[List[str]] = []

    for bloco in blocos_brutos:
        # Remove linhas contendo apenas espaços e faz strip em cada linha.
        # Remove lines that contain only whitespace and strip remaining lines.
        linhas = [linha.strip() for linha in bloco.splitlines() if linha.strip()]
        if not linhas:
            # Ignora blocos vazios.
            # Ignore empty blocks.
            continue
        blocos_processados.append(linhas)

    return blocos_processados


def _texto_de_bloco(linhas_bloco: List[str]) -> str:
    """
    Dado um bloco de linhas de legenda, remove número e timestamp,
    retornando apenas o texto.

    English:
    Given a subtitle block (list of lines), removes index and timestamp lines,
    returning only the subtitle text.
    """
    # Faz uma cópia para não modificar a lista original.
    # Make a copy to avoid modifying the original list.
    linhas = list(linhas_bloco)

    # Remove número do bloco, se existir (primeira linha só com dígitos).
    # Remove block index if present (first line with only digits).
    if linhas and linhas[0].isdigit():
        linhas.pop(0)

    # Remove linha de timestamp, se existir (usa regex TIMESTAMP_PATTERN).
    # Remove timestamp line if present (using TIMESTAMP_PATTERN).
    if linhas and TIMESTAMP_PATTERN.search(linhas[0]):
        linhas.pop(0)

    # O restante são linhas de texto; algumas legendas vêm quebradas em 2+ linhas.
    # The remaining lines are subtitle text; some subtitles are split into 2+ lines.
    return " ".join(linhas).strip()


def _normalizar_pontuacao(texto: str, manter_paragrafos: bool = False) -> str:
    """
    Ajusta espaços antes de pontuação e normaliza espaços em branco.

    Se manter_paragrafos=True, preserva quebras de linha entre parágrafos.

    English:
    Adjusts spaces before punctuation and normalizes whitespace.

    If manter_paragrafos=True, preserves line breaks between paragraphs.
    """
    # Remove espaços antes de sinais de pontuação: "texto ." -> "texto."
    # Remove spaces before punctuation: "text ." -> "text."
    texto = re.sub(r"\s+([.,!?;:])", r"\1", texto)

    if not manter_paragrafos:
        # Modo "texto corrido": comprime todos os espaços/brancos em um só.
        # "Single block" mode: compress all whitespace to a single space.
        texto = re.sub(r"\s+", " ", texto)
        return texto.strip()

    # Modo com parágrafos: trata linha a linha, mantendo quebras de linha.
    # Paragraph mode: process line by line, preserving line breaks.
    linhas = texto.splitlines()
    linhas_tratadas = []

    for linha in linhas:
        # Normaliza espaços e tabs dentro da linha.
        # Normalize spaces and tabs inside each line.
        linha = re.sub(r"[ \t]+", " ", linha).strip()
        linhas_tratadas.append(linha)

    texto = "\n".join(linhas_tratadas)

    # Garante que não haja mais que uma linha vazia entre parágrafos.
    # Ensure no more than one blank line between paragraphs.
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    return texto.strip()


def processar_srt(
    arquivo_srt: str | Path, arquivo_saida: Optional[str | Path] = None
) -> Optional[str]:
    """
    Converte um arquivo SRT em texto corrido, removendo números e timestamps.

    Args:
        arquivo_srt: Caminho para o arquivo SRT de entrada.
        arquivo_saida: Caminho para o arquivo de texto de saída (opcional).

    Returns:
        Texto corrido extraído do SRT ou None em caso de erro.

    English:
    Converts an SRT file into continuous text, removing indices and timestamps.

    Args:
        arquivo_srt: Path to the input SRT file.
        arquivo_saida: Optional path to the output text file.

    Returns:
        The extracted plain text, or None on error.
    """
    caminho = Path(arquivo_srt)
    conteudo = _ler_arquivo_srt(caminho)
    if conteudo is None:
        # Falha na leitura/decodificação.
        # Failed to read/decode file.
        return None

    # Divide em blocos de legenda e extrai apenas o texto de cada bloco.
    # Split into subtitle blocks and extract only text from each block.
    blocos = _extrair_blocos_legenda(conteudo)
    textos = [_texto_de_bloco(bloco) for bloco in blocos]
    # Remove blocos vazios.
    # Remove empty entries.
    textos = [t for t in textos if t]

    # Junta todos os blocos em uma única string.
    # Join all blocks into a single string.
    texto_corrido = " ".join(textos)
    texto_corrido = _normalizar_pontuacao(texto_corrido, manter_paragrafos=False)

    if arquivo_saida:
        try:
            # Garante quebra de linha no final do arquivo (boa prática em Unix).
            # Ensure a trailing newline at end of file (good Unix practice).
            Path(arquivo_saida).write_text(texto_corrido + "\n", encoding="utf-8")
            print(f"Texto salvo em: {arquivo_saida}")
            # Text saved at: <path>
        except OSError as e:
            print(f"Erro ao salvar arquivo '{arquivo_saida}': {e}")
            # Error while writing output file.

    return texto_corrido


def processar_srt_com_paragrafos(
    arquivo_srt: str | Path, arquivo_saida: Optional[str | Path] = None
) -> Optional[str]:
    """
    Converte um arquivo SRT em texto, mantendo uma quebra de parágrafo
    para cada bloco de legenda.

    English:
    Converts an SRT file into text, keeping one paragraph break
    for each subtitle block.
    """
    caminho = Path(arquivo_srt)
    conteudo = _ler_arquivo_srt(caminho)
    if conteudo is None:
        return None

    # Mesma lógica de blocos, mas depois junta com duas quebras de linha.
    # Same block logic, but join with two newlines between paragraphs.
    blocos = _extrair_blocos_legenda(conteudo)
    textos = [_texto_de_bloco(bloco) for bloco in blocos]
    textos = [t for t in textos if t]

    # Cada bloco vira um parágrafo separado por linha em branco.
    # Each block becomes a paragraph separated by a blank line.
    texto_final = "\n\n".join(textos)
    texto_final = _normalizar_pontuacao(texto_final, manter_paragrafos=True)

    if arquivo_saida:
        try:
            # Garante quebra de linha ao final.
            # Ensure trailing newline.
            Path(arquivo_saida).write_text(texto_final + "\n", encoding="utf-8")
            print(f"Texto com parágrafos salvo em: {arquivo_saida}")
            # Text with paragraphs saved at: <path>
        except OSError as e:
            print(f"Erro ao salvar arquivo '{arquivo_saida}': {e}")
            # Error while writing output file.

    return texto_final


def main(argv: Optional[list[str]] = None) -> int:
    """
    Função principal para execução via linha de comando.

    English:
    Main entry point for command-line execution.
    """
    parser = argparse.ArgumentParser(
        description="Converter arquivo SRT para texto corrido ou com parágrafos. "
                    "Convert SRT files to plain text (single block or paragraphs)."
    )
    parser.add_argument(
        "arquivo_srt",
        help="Caminho para o arquivo SRT / Path to the SRT file"
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="ARQUIVO",
        help=(
            "Arquivo de saída (opcional). "
            "Se omitido, será usado o mesmo nome do SRT com extensão .txt. "
            "Optional output file. If omitted, the SRT name with .txt extension is used."
        ),
    )
    parser.add_argument(
        "-p",
        "--paragrafos",
        action="store_true",
        help=(
            "Manter estrutura de parágrafos (um por bloco de legenda). "
            "Keep paragraph structure (one per subtitle block)."
        ),
    )

    args = parser.parse_args(argv)

    caminho_srt = Path(args.arquivo_srt)
    if not caminho_srt.exists():
        print(f"Erro: Arquivo '{caminho_srt}' não encontrado.")
        # Error: SRT file not found.
        return 1

    # <<< NOVO COMPORTAMENTO >>>
    # Se não foi passado -o/--output, gera automaticamente nome .txt.
    # If -o/--output is not provided, automatically use SRT name with .txt.
    if args.output:
        caminho_saida = Path(args.output)
    else:
        caminho_saida = caminho_srt.with_suffix(".txt")

    # Escolhe função de conversão com ou sem parágrafos.
    # Choose conversion function: with or without paragraphs.
    if args.paragrafos:
        resultado = processar_srt_com_paragrafos(caminho_srt, caminho_saida)
    else:
        resultado = processar_srt(caminho_srt, caminho_saida)

    if resultado is None:
        print("Falha ao processar o arquivo SRT. / Failed to process SRT file.")
        return 1

    # Não imprime mais o texto na tela nem o cabeçalho "TEXTO EXTRAÍDO".
    # Does not print the extracted text or any header to stdout anymore.
    return 0


def interface_simples() -> None:
    """
    Interface simples para uso interativo em modo texto.

    English:
    Simple interactive text-mode interface.
    """
    print("=== CONVERSOR SRT PARA TEXTO ===")
    print("=== SRT TO TEXT CONVERTER ===")

    while True:
        print("\nOpções / Options:")
        print("1. Converter SRT para texto corrido / Single-block text")
        print("2. Converter mantendo parágrafos / Keep paragraphs")
        print("3. Sair / Exit")

        opcao = input("\nEscolha uma opção (1-3): / Choose an option (1-3): ").strip()

        if opcao == "3":
            # Sai do loop e encerra a interface.
            # Exit loop and finish interface.
            break
        elif opcao in {"1", "2"}:
            arquivo_srt = input("Caminho do arquivo SRT / SRT file path: ").strip()
            caminho = Path(arquivo_srt)

            if not caminho.exists():
                print("Arquivo não encontrado! / File not found!")
                continue

            salvar = input("Salvar em arquivo? (s/n) / Save to file? (y/n): ").strip().lower()
            arquivo_saida: Optional[Path] = None

            if salvar in {"s", "sim", "y", "yes"}:
                nome_saida = input("Nome do arquivo de saída (opcional) / Output filename (optional): ").strip()
                if not nome_saida:
                    # Baseia no nome original, sem a extensão, adicionando _texto.txt.
                    # Use original name (without extension) + _texto.txt.
                    nome_saida = caminho.with_suffix("").name + "_texto.txt"
                arquivo_saida = Path(nome_saida)

            if opcao == "1":
                resultado = processar_srt(caminho, arquivo_saida)
            else:
                resultado = processar_srt_com_paragrafos(caminho, arquivo_saida)

            if resultado and not arquivo_saida:
                # Imprime só o texto, sem moldura.
                # Print only the resulting text, without decorative headers.
                print()
                print(resultado)

        else:
            print("Opção inválida! / Invalid option!")


if __name__ == "__main__":
    # Se recebeu argumentos na linha de comando, usa main().
    # If command-line arguments are provided, use main().
    if len(sys.argv) > 1:
        raise SystemExit(main())
    else:
        # Senão, entra no modo interativo.
        # Otherwise, start the interactive interface.
        interface_simples()
