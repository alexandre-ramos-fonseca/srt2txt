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
"""


from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from typing import List, Optional


# Padrão de timestamp típico de SRT (00:00:01,000 --> 00:00:03,000)
TIMESTAMP_PATTERN = re.compile(
    r"\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}"
)


def _ler_arquivo_srt(caminho: Path) -> Optional[str]:
    """
    Lê um arquivo SRT tentando UTF-8 e, em caso de falha, Latin-1.
    Retorna o conteúdo como string ou None em caso de erro.
    """
    for encoding in ("utf-8", "latin-1"):
        try:
            return caminho.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            print(f"Erro: Arquivo '{caminho}' não encontrado.")
            return None
        except OSError as e:
            print(f"Erro ao ler arquivo '{caminho}': {e}")
            return None

    print(f"Erro: não foi possível decodificar '{caminho}' como UTF-8 nem Latin-1.")
    return None


def _extrair_blocos_legenda(conteudo: str) -> List[List[str]]:
    """
    Divide o conteúdo do SRT em blocos de legenda.
    Cada bloco é retornado como uma lista de linhas (sem quebras de linha).
    """
    # separa por linhas em branco (uma ou mais)
    blocos_brutos = re.split(r"\n\s*\n", conteudo.strip(), flags=re.MULTILINE)
    blocos_processados: List[List[str]] = []

    for bloco in blocos_brutos:
        # remove linhas só de espaços
        linhas = [linha.strip() for linha in bloco.splitlines() if linha.strip()]
        if not linhas:
            continue
        blocos_processados.append(linhas)

    return blocos_processados


def _texto_de_bloco(linhas_bloco: List[str]) -> str:
    """
    Dado um bloco de linhas de legenda, remove número e timestamp,
    retornando apenas o texto.
    """
    linhas = list(linhas_bloco)  # cópia

    # Remove número do bloco, se existir
    if linhas and linhas[0].isdigit():
        linhas.pop(0)

    # Remove linha de timestamp, se existir
    if linhas and TIMESTAMP_PATTERN.search(linhas[0]):
        linhas.pop(0)

    # O restante são linhas de texto (uma legenda pode vir quebrada em 2+ linhas)
    return " ".join(linhas).strip()


def _normalizar_pontuacao(texto: str, manter_paragrafos: bool = False) -> str:
    """
    Ajusta espaços antes de pontuação e normaliza espaços em branco.

    Se manter_paragrafos=True, preserva quebras de linha entre parágrafos.
    """
    # Remove espaços antes de pontuação
    texto = re.sub(r"\s+([.,!?;:])", r"\1", texto)

    if not manter_paragrafos:
        # Tudo em um bloco só
        texto = re.sub(r"\s+", " ", texto)
        return texto.strip()

    # Modo com parágrafos: trata linha a linha
    linhas = texto.splitlines()
    linhas_tratadas = []

    for linha in linhas:
        # Normaliza apenas espaços/tabs dentro da linha
        linha = re.sub(r"[ \t]+", " ", linha).strip()
        linhas_tratadas.append(linha)

    texto = "\n".join(linhas_tratadas)

    # Limita linhas em branco consecutivas (no máx. 1 em branco -> parágrafo)
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
    """
    caminho = Path(arquivo_srt)
    conteudo = _ler_arquivo_srt(caminho)
    if conteudo is None:
        return None

    blocos = _extrair_blocos_legenda(conteudo)
    textos = [_texto_de_bloco(bloco) for bloco in blocos]
    textos = [t for t in textos if t]

    texto_corrido = " ".join(textos)
    texto_corrido = _normalizar_pontuacao(texto_corrido, manter_paragrafos=False)

    if arquivo_saida:
        try:
            # Garante quebra de linha no final do arquivo
            Path(arquivo_saida).write_text(texto_corrido + "\n", encoding="utf-8")
            print(f"Texto salvo em: {arquivo_saida}")
        except OSError as e:
            print(f"Erro ao salvar arquivo '{arquivo_saida}': {e}")


    return texto_corrido


def processar_srt_com_paragrafos(
    arquivo_srt: str | Path, arquivo_saida: Optional[str | Path] = None
) -> Optional[str]:
    """
    Converte um arquivo SRT em texto, mantendo uma quebra de parágrafo
    para cada bloco de legenda.
    """
    caminho = Path(arquivo_srt)
    conteudo = _ler_arquivo_srt(caminho)
    if conteudo is None:
        return None

    blocos = _extrair_blocos_legenda(conteudo)
    textos = [_texto_de_bloco(bloco) for bloco in blocos]
    textos = [t for t in textos if t]

    texto_final = "\n\n".join(textos)
    texto_final = _normalizar_pontuacao(texto_final, manter_paragrafos=True)

    if arquivo_saida:
        try:
            # Também garante quebra de linha ao final
            Path(arquivo_saida).write_text(texto_final + "\n", encoding="utf-8")
            print(f"Texto com parágrafos salvo em: {arquivo_saida}")
        except OSError as e:
            print(f"Erro ao salvar arquivo '{arquivo_saida}': {e}")


    return texto_final


def main(argv: Optional[list[str]] = None) -> int:
    """Função principal para execução via linha de comando."""
    parser = argparse.ArgumentParser(
        description="Converter arquivo SRT para texto corrido ou com parágrafos."
    )
    parser.add_argument("arquivo_srt", help="Caminho para o arquivo SRT")
    parser.add_argument(
        "-o",
        "--output",
        metavar="ARQUIVO",
        help=(
            "Arquivo de saída (opcional). "
            "Se omitido, será usado o mesmo nome do SRT com extensão .txt."
        ),
    )
    parser.add_argument(
        "-p",
        "--paragrafos",
        action="store_true",
        help="Manter estrutura de parágrafos (um por bloco de legenda).",
    )

    args = parser.parse_args(argv)

    caminho_srt = Path(args.arquivo_srt)
    if not caminho_srt.exists():
        print(f"Erro: Arquivo '{caminho_srt}' não encontrado.")
        return 1

    # <<< NOVO COMPORTAMENTO >>>
    # Se não foi passado -o/--output, gera automaticamente nome .txt
    if args.output:
        caminho_saida = Path(args.output)
    else:
        caminho_saida = caminho_srt.with_suffix(".txt")

    if args.paragrafos:
        resultado = processar_srt_com_paragrafos(caminho_srt, caminho_saida)
    else:
        resultado = processar_srt(caminho_srt, caminho_saida)

    if resultado is None:
        print("Falha ao processar o arquivo SRT.")
        return 1

    # Não imprime mais o texto na tela nem o cabeçalho "TEXTO EXTRAÍDO"
    return 0


def interface_simples() -> None:
    """Interface simples para uso interativo."""
    print("=== CONVERSOR SRT PARA TEXTO ===")

    while True:
        print("\nOpções:")
        print("1. Converter SRT para texto corrido")
        print("2. Converter mantendo parágrafos")
        print("3. Sair")

        opcao = input("\nEscolha uma opção (1-3): ").strip()

        if opcao == "3":
            break
        elif opcao in {"1", "2"}:
            arquivo_srt = input("Caminho do arquivo SRT: ").strip()
            caminho = Path(arquivo_srt)

            if not caminho.exists():
                print("Arquivo não encontrado!")
                continue

            salvar = input("Salvar em arquivo? (s/n): ").strip().lower()
            arquivo_saida: Optional[Path] = None

            if salvar in {"s", "sim"}:
                nome_saida = input("Nome do arquivo de saída: ").strip()
                if not nome_saida:
                    # baseia no nome original, sem a extensão
                    nome_saida = caminho.with_suffix("").name + "_texto.txt"
                arquivo_saida = Path(nome_saida)

            if opcao == "1":
                resultado = processar_srt(caminho, arquivo_saida)
            else:
                resultado = processar_srt_com_paragrafos(caminho, arquivo_saida)

            if resultado and not arquivo_saida:
                # Imprime só o texto, sem moldura
                print()
                print(resultado)

        else:
            print("Opção inválida!")


if __name__ == "__main__":
    # Se recebeu argumentos, usa linha de comando
    if len(sys.argv) > 1:
        raise SystemExit(main())
    else:
        # Senão, usa interface interativa
        interface_simples()
