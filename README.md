# 📝 SRT → TXT Converter

This project converts **.srt** subtitle files into **.txt** files, removing index numbers, timestamps, and merging broken lines.  
It can also preserve paragraphs corresponding to the original subtitle blocks.

---

## 🚀 Features

- Automatically converts `.srt` files to `.txt`
- Removes:
  - subtitle index numbers
  - timestamps (`00:00:01,000 --> 00:00:03,000`)
- Joins multi-line subtitles into continuous text
- **Optional:** keeps paragraph structure based on SRT blocks (`-p`)
- Automatically detects UTF-8 or Latin-1 encodings
- Generates output file with **the same name as the SRT** (e.g., `video.srt → video.txt`)
- Includes an optional interactive interface

---

## 📌 Command-line usage

### Convert a file (generates `file.txt`)

```bash
python srt2txt.py subtitles.srt
```

### Convert while keeping paragraphs

```bash
python srt2txt.py subtitles.srt -p
```

### Specify an output file manually

```bash
python srt2txt.py subtitles.srt -o output.txt
```

---

## 📋 Examples

### Input (`example.srt`)

```
1
00:00:01,000 --> 00:00:02,000
Hello, everyone.

2
00:00:02,500 --> 00:00:04,000
Welcome!
```

### Output (`example.txt`)

```
Hello, everyone. Welcome!
```

### Output with `-p`

```
Hello, everyone.

Welcome!
```

---

## 🖥️ Interactive interface

Run without arguments:

```bash
python srt2txt.py
```

The script enters a simple terminal-based interactive mode.

---

## ⚙️ Requirements

- Python **3.8+**

---

## 🔧 Possible future improvements

- Remove subtitle tags such as `[MUSIC]`, `<i>...</i>`, `(laughs)`  
- Batch conversion support (`*.srt`)  
- Pipe support (`cat video.srt | python srt2txt.py`)  
- Whisper integration (transcribe audio + generate SRT + convert)

---

## 📝 License

This project is distributed under the **MIT** license.

You are free to use, copy, modify, merge, publish, distribute, and even sell
this software, provided that the original copyright notice is preserved.

See the `LICENSE` file for more details.
