# -*- coding: utf-8 -*-
"""
PPTX, DOCX va PDF fayllarni AI-generatsiya qilingan matn, rasmlar va
ko'p tillilik bilan yaratuvchi funksiyalar.
"""

import os
from pptx import Presentation
from pptx.util import Inches

from docx import Document

from fpdf import FPDF

from ai_helper import generate_section_text
from image_helper import generate_slide_image
from locales import t


def _is_conclusion_point(point: str, language: str) -> bool:
    """Foydalanuvchi o'zi 'Xulosa'/'Заключение'/'Conclusion' nomli bo'lim
    kiritgan bo'lsa, bot buni ikkilantirib qo'shmasligi uchun tekshiradi."""
    conclusion_words = {"xulosa", "заключение", "conclusion"}
    return point.strip().lower() in conclusion_words


# ==================== PPTX (Slayd) ====================
def create_pptx(topic: str, points: list, output_path: str, language: str = "uz"):
    prs = Presentation()
    slide_width_in = prs.slide_width / 914400  # EMU -> inches

    # Titul slaydi
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    slide.shapes.title.text = topic
    slide.placeholders[1].text = t(language, "subtitle")

    # Har bir nuqta uchun alohida slayd + AI matn + rasm
    bullet_layout = prs.slide_layouts[1]
    for point in points:
        slide = prs.slides.add_slide(bullet_layout)
        slide.shapes.title.text = point

        ai_text = generate_section_text(topic, point, language)
        body = slide.placeholders[1]
        body.text_frame.text = ai_text

        # Rasm uchun joy ajratib, matn qutisini TORAYTIRAMIZ (overlap bo'lmasligi uchun)
        img_width = Inches(1.8)
        img_margin_right = Inches(0.5)
        img_left = Inches(slide_width_in) - img_width - img_margin_right

        # Matn qutisi rasm boshlanishidan oldin tugashi kerak
        text_right_edge = img_left - Inches(0.3)
        body.width = text_right_edge - body.left

        try:
            img_path = generate_slide_image(point)
            slide.shapes.add_picture(
                img_path, img_left, Inches(1.5), width=img_width, height=Inches(1.0)
            )
        except Exception:
            pass  # rasm qo'shilmasa ham fayl yaratilishda davom etadi

    # Xulosa slaydi — foydalanuvchi allaqachon shu nomli bo'lim kiritgan bo'lsa, qo'shmaymiz
    if not points or not _is_conclusion_point(points[-1], language):
        slide = prs.slides.add_slide(bullet_layout)
        slide.shapes.title.text = t(language, "conclusion_title")
        slide.placeholders[1].text = t(language, "conclusion_text")

    prs.save(output_path)


# ==================== DOCX (Mustaqil ish) ====================
def create_docx(topic: str, points: list, output_path: str, language: str = "uz"):
    doc = Document()

    doc.add_heading(topic, level=0)
    doc.add_paragraph("")

    doc.add_heading(t(language, "plan_title"), level=1)
    for i, point in enumerate(points, 1):
        doc.add_paragraph(f"{i}. {point}")

    doc.add_page_break()

    for point in points:
        doc.add_heading(point, level=1)
        ai_text = generate_section_text(topic, point, language)
        doc.add_paragraph(ai_text)
        doc.add_paragraph("")

    if not points or not _is_conclusion_point(points[-1], language):
        doc.add_heading(t(language, "conclusion_title"), level=1)
        doc.add_paragraph(t(language, "conclusion_text"))

    doc.save(output_path)


# ==================== PDF ====================
class PDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"{self.page_no()}", align="C")


def create_pdf(topic: str, points: list, output_path: str, language: str = "uz"):
    pdf = PDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.multi_cell(0, 15, topic, align="C")
    pdf.ln(10)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, t(language, "plan_title"), ln=True)
    pdf.set_font("Helvetica", "", 12)
    for i, point in enumerate(points, 1):
        pdf.cell(0, 8, f"{i}. {point}", ln=True)

    pdf.add_page()

    for point in points:
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, point, ln=True)
        pdf.set_font("Helvetica", "", 12)
        ai_text = generate_section_text(topic, point, language)
        pdf.multi_cell(0, 8, ai_text)
        pdf.ln(5)

    if not points or not _is_conclusion_point(points[-1], language):
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, t(language, "conclusion_title"), ln=True)
        pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(0, 8, t(language, "conclusion_text"))

    pdf.output(output_path)
