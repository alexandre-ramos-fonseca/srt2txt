# 📝 Conversor SRT → TXT

Este projeto converte arquivos **.srt** (legendas) em arquivos **.txt**, removendo números, timestamps e unificando linhas.  
Também é possível manter parágrafos correspondentes aos blocos de legenda originais.

---

## 🚀 Funcionalidades

- Converte arquivos `.srt` em `.txt` automaticamente  
- Remove:
  - números das legendas
  - timestamps (`00:00:01,000 --> 00:00:03,000`)
- Junta linhas quebradas em texto corrido
- **Opcional:** mantém parágrafos conforme blocos do SRT (`-p`)
- Detecta automaticamente codificação UTF-8 ou Latin-1
- Gera arquivo de saída com **o mesmo nome do SRT** (ex.: `video.srt → video.txt`)
- Possui interface interativa opcional

---

## 📦 Instalação

Nenhuma dependência externa é necessária além do Python 3.

Clone o repositório:

```bash
git clone https://seu_repositorio_aqui.git
cd conversor-srt
```

Ou apenas baixe o arquivo `srt2txt.py`.

---

## 📌 Uso via linha de comando

### Converter um arquivo (gera `arquivo.txt`)

```bash
python srt2txt.py legenda.srt
```

### Converter mantendo parágrafos

```bash
python srt2txt.py legenda.srt -p
```

### Especificar arquivo de saída manualmente

```bash
python srt2txt.py legenda.srt -o saida.txt
```

---

## 📋 Exemplos

### Entrada (`exemplo.srt`)

```
1
00:00:01,000 --> 00:00:02,000
Olá, pessoal.

2
00:00:02,500 --> 00:00:04,000
Sejam bem-vindos!
```

### Saída (`exemplo.txt`)

```
Olá, pessoal. Sejam bem-vindos!
```

### Saída com `-p`

```
Olá, pessoal.

Sejam bem-vindos!
```

---

## 🖥️ Interface interativa

Executar sem argumentos:

```bash
python srt2txt.py
```

---

## 📚 Estrutura do projeto

```
srt2txt.py
README.md
```

---

## ⚙️ Requisitos

- Python **3.8+**

---

## 🔧 Possíveis melhorias futuras

- Remover marcas como `[MÚSICA]`, `<i>...</i>`, `(risos)`  
- Suporte a conversão em lote (`*.srt`)  
- Suporte a pipes (`cat video.srt | python srt2txt.py`)  
- Integração com Whisper (transcrever áudio + gerar SRT + converter)

---

## 📝 Licença

Este projeto é distribuído sob a licença **MIT**.

Você pode usar, copiar, modificar, mesclar, publicar, distribuir e até vender
este software livremente, desde que mantenha o aviso de copyright.

Consulte o arquivo `LICENSE` para mais informações.


