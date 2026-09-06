# -*- coding: utf-8 -*-
"""
Anthropic (Claude) API orqali har bir bo'lim uchun matn generatsiya qilish.

ANTHROPIC_API_KEY environment variable orqali API kalitini bering:
    export ANTHROPIC_API_KEY="sk-ant-..."

Agar kalit berilmagan yoki xatolik yuz bersa, oddiy shablon matn qaytariladi
(bot ishlashda to'xtab qolmasligi uchun).
"""

import os
import logging
from anthropic import Anthropic, APIError

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return None
        _client = Anthropic(api_key=api_key)
    return _client


PROMPTS = {
    "uz": (
        "Sen o'quv materiali yozuvchi yordamchisan. "
        "Mavzu: '{topic}'. Bo'lim: '{section}'.\n"
        "Shu bo'lim uchun 3-5 jumladan iborat, aniq va tushunarli o'zbek tilida "
        "matn yoz. Faqat matnni yoz, boshqa hech narsa qo'shma (sarlavha, "
        "izoh yoki markdown belgilarisiz)."
    ),
    "ru": (
        "Ты помощник по написанию учебных материалов. "
        "Тема: '{topic}'. Раздел: '{section}'.\n"
        "Напиши для этого раздела 3-5 предложений, ясным и понятным русским "
        "языком. Пиши только текст, без заголовков, комментариев или markdown."
    ),
    "en": (
        "You are an assistant writing educational material. "
        "Topic: '{topic}'. Section: '{section}'.\n"
        "Write 3-5 clear sentences in English for this section. "
        "Output only the text, no headings, comments, or markdown."
    ),
}

FALLBACK_TEXT = {
    "uz": "Bu bo'limda '{section}' mavzusi batafsil yoritiladi. "
          "Bu yerga tegishli matn, tahlil va misollarni qo'shishingiz mumkin.",
    "ru": "В этом разделе подробно рассматривается '{section}'. "
          "Здесь вы можете добавить соответствующий текст, анализ и примеры.",
    "en": "This section covers '{section}' in detail. "
          "You can add relevant text, analysis, and examples here.",
}


def generate_section_text(topic: str, section: str, language: str = "uz") -> str:
    """Berilgan mavzu va bo'lim uchun AI yordamida matn yozadi.
    API kaliti bo'lmasa yoki xato bo'lsa, shablon matnni qaytaradi.
    """
    client = _get_client()
    if client is None:
        return FALLBACK_TEXT.get(language, FALLBACK_TEXT["uz"]).format(section=section)

    prompt_template = PROMPTS.get(language, PROMPTS["uz"])
    prompt = prompt_template.format(topic=topic, section=section)

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        text_parts = [
            block.text for block in response.content if block.type == "text"
        ]
        result = " ".join(text_parts).strip()
        return result if result else FALLBACK_TEXT[language].format(section=section)
    except APIError as e:
        logger.warning(f"Anthropic API xatosi: {e}")
        return FALLBACK_TEXT.get(language, FALLBACK_TEXT["uz"]).format(section=section)
    except Exception as e:
        logger.warning(f"Kutilmagan xatolik (AI matn): {e}")
        return FALLBACK_TEXT.get(language, FALLBACK_TEXT["uz"]).format(section=section)
