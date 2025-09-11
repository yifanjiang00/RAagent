import os

def extract_text(file_path: str) -> str:
    """
    根据文件类型自动抽取文本内容
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    try:
        if ext in ['.txt', '.md', '.csv', '.json', '.xml', '.html', '.htm']:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        elif ext == '.pdf':
            return extract_pdf(file_path)

        elif ext in ['.docx']:
            return extract_docx(file_path)

        else:
            return f"[不支持的文件类型: {ext}]"

    except Exception as e:
        return f"[读取文件失败: {str(e)}]"


def extract_pdf(file_path: str) -> str:
    """
    提取PDF文件文本
    """
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        text = []
        for page in reader.pages:
            text.append(page.extract_text() or "")
        return "\n".join(text).strip()
    except ImportError:
        return "[未安装 PyPDF2，无法解析PDF]"
    except Exception as e:
        return f"[PDF解析失败: {str(e)}]"


def extract_docx(file_path: str) -> str:
    """
    提取Word(docx)文件文本
    """
    try:
        import docx
        doc = docx.Document(file_path)
        text = []
        for para in doc.paragraphs:
            if para.text.strip():
                text.append(para.text)
        return "\n".join(text).strip()
    except ImportError:
        return "[未安装 python-docx，无法解析DOCX]"
    except Exception as e:
        return f"[DOCX解析失败: {str(e)}]"
