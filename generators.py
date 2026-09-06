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


# ==================== PPTX (Slayd) ====================
def create_pptx(topic: str, points: list, output_path: str, language: str = "uz"):
    prs = Presentation()

    # Titul slaydi (rasm bilan)
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

        # O'ng tomonga kichik dekorativ rasm qo'shish
        try:
            img_path = generate_slide_image(point)
            slide.shapes.add_picture(
                img_path, Inches(7.8), Inches(1.5), width=Inches(1.8), height=Inches(1.0)
            )
        except Exception:
            pass  # rasm qo'shilmasa ham fayl yaratilishda davom etadi

    # Xulosa slaydi
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

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, t(language, "conclusion_title"), ln=True)
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(0, 8, t(language, "conclusion_text"))

    pdf.output(output_path)
