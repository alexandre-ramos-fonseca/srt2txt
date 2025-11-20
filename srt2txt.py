#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para converter arquivos SRT em texto corrido
"""

import re
import os
import argparse
import sys

def processar_srt(arquivo_srt, arquivo_saida=None):
    """
    Converte um arquivo SRT em texto corrido, removendo números e timestamps.

    Args:
        arquivo_srt (str): Caminho para o arquivo SRT de entrada
        arquivo_saida (str, optional): Caminho para o arquivo de texto de saída

    Returns:
        str: Texto corrido extraído do SRT
    """
    try:
        with open(arquivo_srt, 'r', encoding='utf-8') as file:
            linhas = file.readlines()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{arquivo_srt}' não encontrado.")
        return None
    except UnicodeDecodeError:
        # Tenta com encoding alternativo se UTF-8 falhar
        try:
            with open(arquivo_srt, 'r', encoding='latin-1') as file:
                linhas = file.readlines()
        except Exception as e:
            print(f"Erro ao ler arquivo: {e}")
            return None

    texto_final = []
    i = 0

    while i < len(linhas):
        linha = linhas[i].strip()

        # Pula números de sequência
        if linha.isdigit():
            i += 1
            continue

        # Pula timestamps
        if '-->' in linha:
            i += 1
            continue

        # Adiciona texto da legenda
        if linha:
            texto_final.append(linha)

        i += 1

    # Junta tudo em texto corrido
    texto_corrido = ' '.join(texto_final)

    # Corrige pontuação
    texto_corrido = re.sub(r'\s+([.,!?;:])', r'\1', texto_corrido)
    texto_corrido = re.sub(r'\s+', ' ', texto_corrido)
    texto_corrido = texto_corrido.strip()

    # Salva em arquivo se especificado
    if arquivo_saida:
        try:
            with open(arquivo_saida, 'w', encoding='utf-8') as output:
                output.write(texto_corrido)
            print(f"Texto salvo em: {arquivo_saida}")
        except Exception as e:
            print(f"Erro ao salvar arquivo: {e}")

    return texto_corrido

def processar_srt_com_paragrafos(arquivo_srt, arquivo_saida=None):
    """
    Versão alternativa que mantém parágrafos baseados nas quebras do SRT.
    """
    try:
        with open(arquivo_srt, 'r', encoding='utf-8') as file:
            conteudo = file.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{arquivo_srt}' não encontrado.")
        return None
    except UnicodeDecodeError:
        try:
            with open(arquivo_srt, 'r', encoding='latin-1') as file:
                conteudo = file.read()
        except Exception as e:
            print(f"Erro ao ler arquivo: {e}")
            return None

    # Divide por blocos de legenda (separados por linha vazia)
    blocos = conteudo.strip().split('\n\n')
    textos = []

    for bloco in blocos:
        linhas = bloco.split('\n')
        if len(linhas) >= 3:  # Número, timestamp e pelo menos uma linha de texto
            # Pega as linhas de texto (ignora as duas primeiras: número e timestamp)
            texto_bloco = ' '.join(linhas[2:])
            if texto_bloco.strip():
                textos.append(texto_bloco.strip())

    texto_final = '\n\n'.join(textos)

    # Corrige pontuação
    texto_final = re.sub(r'\s+([.,!?;:])', r'\1', texto_final)
    texto_final = re.sub(r'\s+', ' ', texto_final)

    if arquivo_saida:
        try:
            with open(arquivo_saida, 'w', encoding='utf-8') as output:
                output.write(texto_final)
            print(f"Texto com parágrafos salvo em: {arquivo_saida}")
        except Exception as e:
            print(f"Erro ao salvar arquivo: {e}")

    return texto_final

def main():
    """Função principal para execução via linha de comando."""
    parser = argparse.ArgumentParser(description='Converter arquivo SRT para texto corrido')
    parser.add_argument('arquivo_srt', help='Caminho para o arquivo SRT')
    parser.add_argument('-o', '--output', help='Arquivo de saída (opcional)')
    parser.add_argument('-p', '--paragrafos', action='store_true',
                       help='Manter estrutura de parágrafos')

    args = parser.parse_args()

    # Verifica se arquivo existe
    if not os.path.exists(args.arquivo_srt):
        print(f"Erro: Arquivo '{args.arquivo_srt}' não encontrado.")
        sys.exit(1)

    # Processa o arquivo
    if args.paragrafos:
        resultado = processar_srt_com_paragrafos(args.arquivo_srt, args.output)
    else:
        resultado = processar_srt(args.arquivo_srt, args.output)

    if resultado:
        if not args.output:  # Se não salvou em arquivo, mostra na tela
            print("\n" + "="*50)
            print("TEXTO EXTRAÍDO:")
            print("="*50)
            print(resultado)
    else:
        print("Falha ao processar o arquivo SRT.")
        sys.exit(1)

def interface_simples():
    """Interface simples para uso interativo."""
    print("=== CONVERSOR SRT PARA TEXTO ===")

    while True:
        print("\nOpções:")
        print("1. Converter SRT para texto corrido")
        print("2. Converter mantendo parágrafos")
        print("3. Sair")

        opcao = input("\nEscolha uma opção (1-3): ").strip()

        if opcao == '3':
            break
        elif opcao in ['1', '2']:
            arquivo_srt = input("Caminho do arquivo SRT: ").strip()

            if not os.path.exists(arquivo_srt):
                print("Arquivo não encontrado!")
                continue

            salvar = input("Salvar em arquivo? (s/n): ").strip().lower()
            arquivo_saida = None

            if salvar in ['s', 'sim']:
                arquivo_saida = input("Nome do arquivo de saída: ").strip()
                if not arquivo_saida:
                    arquivo_saida = arquivo_srt.replace('.srt', '_texto.txt')

            if opcao == '1':
                resultado = processar_srt(arquivo_srt, arquivo_saida)
            else:
                resultado = processar_srt_com_paragrafos(arquivo_srt, arquivo_saida)

            if resultado and not arquivo_saida:
                print("\n" + "="*50)
                print("RESULTADO:")
                print("="*50)
                print(resultado)

        else:
            print("Opção inválida!")

if __name__ == "__main__":
    # Se recebeu argumentos, usa linha de comando
    if len(sys.argv) > 1:
        main()
    else:
        # Senão, usa interface interativa
        interface_simples()
