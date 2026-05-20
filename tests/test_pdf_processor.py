"""Tests for pdf_processor — uses programmatically generated PDFs (no external data)."""
import fitz
import tempfile
import os
from src.pdf_processor import (
    add_text_right,
    add_text_center,
    find_renamed_file,
    build_remark_and_signature,
    process_pdf,
    RIGHT_MARGIN,
    Y_REF,
    Y_SIG,
    Y_RMK,
    Y_PGN,
)


def _make_test_pdf(rotation=0):
    """Create a minimal single-page PDF with given rotation."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.set_rotation(rotation)
    return doc


def test_add_text_right_rot0():
    doc = _make_test_pdf(rotation=0)
    page = doc[0]
    add_text_right(page, "TEST-001", Y_REF, fontsize=12)
    # Text should have been inserted (no error = pass)
    # Verify text is present on page (at least one text block)
    blocks = page.get_text("dict")["blocks"]
    assert len(blocks) > 0


def test_add_text_right_rot270():
    doc = _make_test_pdf(rotation=270)
    page = doc[0]
    add_text_right(page, "TEST-002", Y_REF, fontsize=12)
    blocks = page.get_text("dict")["blocks"]
    assert len(blocks) > 0


def test_add_text_right_rot90():
    doc = _make_test_pdf(rotation=90)
    page = doc[0]
    add_text_right(page, "TEST-003", Y_REF, fontsize=12)
    blocks = page.get_text("dict")["blocks"]
    assert len(blocks) > 0


def test_add_text_center_rot0():
    doc = _make_test_pdf(rotation=0)
    page = doc[0]
    add_text_center(page, "Centered Remark", Y_RMK, fontsize=9)
    blocks = page.get_text("dict")["blocks"]
    assert len(blocks) > 0


def test_add_text_center_rot270():
    doc = _make_test_pdf(rotation=270)
    page = doc[0]
    add_text_center(page, "Centered Text", Y_RMK, fontsize=9)
    blocks = page.get_text("dict")["blocks"]
    assert len(blocks) > 0


def test_add_text_center_rot90():
    doc = _make_test_pdf(rotation=90)
    page = doc[0]
    add_text_center(page, "Centered Text", Y_RMK, fontsize=9)
    blocks = page.get_text("dict")["blocks"]
    assert len(blocks) > 0


def test_find_renamed_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a renamed file
        fname = os.path.join(tmpdir, "E100_4050_10_汇丰_2025_15.05.2025.pdf")
        open(fname, 'w').close()

        path, date_str = find_renamed_file(tmpdir, "E100_4050_10_汇丰_2025.pdf")
        assert path is not None
        assert date_str == "15.05.2025"


def test_find_renamed_file_not_found():
    with tempfile.TemporaryDirectory() as tmpdir:
        path, date_str = find_renamed_file(tmpdir, "nonexistent.pdf")
        assert path is None
        assert date_str is None


def test_build_remark_signature_early_date():
    remark, sig = build_remark_and_signature("15.01.2026")
    assert "15.01.2026" in remark
    assert sig == "amber 31.3.2026"


def test_build_remark_signature_late_date():
    remark, sig = build_remark_and_signature("15.05.2026")
    assert "15.05.2026" in remark
    assert sig == "amber 15.05.2026"


def test_build_remark_signature_none_date():
    remark, sig = build_remark_and_signature(None)
    assert remark == "This confirmation is received by express delivery on"
    assert sig == "amber 31.3.2026"


def test_process_pdf_creates_output():
    """End-to-end: create a PDF, process it, verify output exists and has text."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, "test_input.pdf")
        out_path = os.path.join(tmpdir, "test_output.pdf")

        # Create a two-page PDF
        doc = fitz.open()
        doc.new_page(width=595, height=842)
        doc.new_page(width=595, height=842)
        doc.save(src_path)
        doc.close()

        result = process_pdf(src_path, "999", out_path, date_str="15.05.2026")
        assert result is True
        assert os.path.exists(out_path)

        # Verify output
        out_doc = fitz.open(out_path)
        assert out_doc.page_count == 2
        # Page 1 should have text blocks (remark + reference + signature)
        p1_blocks = out_doc[0].get_text("dict")["blocks"]
        assert len(p1_blocks) >= 3
        out_doc.close()


def test_process_pdf_missing_source():
    result = process_pdf("/nonexistent/path.pdf", "999", "/tmp/out.pdf")
    assert result is False


def test_process_pdf_with_rotation():
    """Process a rotated (270) PDF and verify it works."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, "test_rot.pdf")
        out_path = os.path.join(tmpdir, "test_rot_out.pdf")

        doc = fitz.open()
        page = doc.new_page(width=595, height=842)
        page.set_rotation(270)
        doc.save(src_path)
        doc.close()

        result = process_pdf(src_path, "888", out_path, date_str="20.05.2026")
        assert result is True

        out_doc = fitz.open(out_path)
        blocks = out_doc[0].get_text("dict")["blocks"]
        assert len(blocks) >= 3
        out_doc.close()
