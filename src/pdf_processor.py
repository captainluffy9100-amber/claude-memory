"""PDF processing utilities — text positioning with rotation support."""
import fitz
import re
import os
from datetime import datetime

RIGHT_MARGIN = 5
Y_REF = 25
Y_SIG = 47
Y_RMK = 6
Y_PGN = 25

SIGNATURE = "amber 31.3.2026"
REMARK = "This confirmation is received by express delivery on"


def add_text_right(page, text, y_disp, fontsize=12, color=(1, 0, 0)):
    """Right-aligned horizontal text, handles page rotation automatically."""
    text_w = fitz.get_text_length(text, fontname="helv", fontsize=fontsize)
    rot = page.rotation
    mb = page.mediabox
    disp_x = page.rect.width - text_w - RIGHT_MARGIN

    if rot == 270:
        raw_x = mb.width - y_disp
        raw_y = disp_x
        page.insert_text(point=(raw_x, raw_y), text=text,
                         fontsize=fontsize, color=color, fontname="helv",
                         rotate=270)
    elif rot == 90:
        raw_x = y_disp
        raw_y = mb.height - disp_x
        page.insert_text(point=(raw_x, raw_y), text=text,
                         fontsize=fontsize, color=color, fontname="helv",
                         rotate=90)
    else:
        page.insert_text(point=(disp_x, y_disp), text=text,
                         fontsize=fontsize, color=color, fontname="helv")


def add_text_center(page, text, y_disp, fontsize=9, color=(1, 0, 0)):
    """Centered horizontal text, handles page rotation automatically."""
    text_w = fitz.get_text_length(text, fontname="helv", fontsize=fontsize)
    rot = page.rotation
    mb = page.mediabox
    disp_x = (page.rect.width - text_w) / 2

    if rot == 270:
        raw_x = mb.width - y_disp
        raw_y = disp_x
        page.insert_text(point=(raw_x, raw_y), text=text,
                         fontsize=fontsize, color=color, fontname="helv",
                         rotate=270)
    elif rot == 90:
        raw_x = y_disp
        raw_y = mb.height - disp_x
        page.insert_text(point=(raw_x, raw_y), text=text,
                         fontsize=fontsize, color=color, fontname="helv",
                         rotate=90)
    else:
        page.insert_text(point=(disp_x, y_disp), text=text,
                         fontsize=fontsize, color=color, fontname="helv")


def find_renamed_file(output_dir, base_name):
    """Find renamed file like 'base_name_D.M.YYYY.pdf', return (path, date_str)."""
    stem = base_name.replace('.pdf', '')
    pat = re.compile(re.escape(stem) + r'_(\d{1,2}\.\d{1,2}\.\d{4})\.pdf$')
    for fname in os.listdir(output_dir):
        m = pat.match(fname)
        if m:
            return os.path.join(output_dir, fname), m.group(1)
    return None, None


def build_remark_and_signature(date_str):
    """Build remark and signature strings, updating signature if date > 31.3.2026."""
    remark = REMARK
    sig = SIGNATURE
    if date_str:
        remark = f"{REMARK} {date_str}."
        try:
            fdate = datetime.strptime(date_str, "%d.%m.%Y").date()
            sdate = datetime.strptime("31.3.2026", "%d.%m.%Y").date()
            if fdate > sdate:
                sig = f"amber {date_str}"
        except ValueError:
            pass
    return remark, sig


def process_pdf(source_path, ref_num_str, output_path, date_str=None):
    """Add reference, signature, remark and page numbers to a PDF."""
    if not os.path.exists(source_path):
        print(f"  [SKIP] File not found: {source_path}")
        return False

    doc = fitz.open(source_path)
    reference = f"<E100-4050-{ref_num_str}>"

    remark, sig = build_remark_and_signature(date_str)

    for pi in range(doc.page_count):
        page = doc[pi]
        if pi == 0:
            add_text_center(page, remark, Y_RMK, fontsize=9, color=(0.4, 0.7, 1.0))
            add_text_right(page, reference, Y_REF, fontsize=12)
            add_text_right(page, sig, Y_SIG, fontsize=12)
        else:
            add_text_right(page, f"/{pi}", Y_PGN, fontsize=12)

    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    return True
