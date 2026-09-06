# -*- coding: utf-8 -*-
"""
Ko'p tillilik (uz/ru/en) uchun UI matnlari va AI prompt shablonlari.
"""

TEXTS = {
    "uz": {
        "choose_lang": "Tilni tanlang / Выберите язык / Choose language:",
        "welcome": (
            "Salom! 👋\n\n"
            "Men sizga *slayd*, *mustaqil ish* yoki *PDF* fayl tayyorlab beraman "
            "(matn AI yordamida yoziladi).\n\n"
            "Qaysi turdagi fayl kerak?"
        ),
        "ask_topic": "Mavzuni yozing (masalan: 'Sun'iy intellekt tarixi'):",
        "ask_points": (
            "Endi asosiy bo'limlarni/nuqtalarni yuboring.\n"
            "Har birini YANGI QATORDA yozing.\n\n"
            "Masalan:\n"
            "Kirish\n"
            "Asosiy qism\n"
            "Xulosa"
        ),
        "generating": "⏳ AI matn yozmoqda va fayl tayyorlanmoqda, biroz kuting...",
        "done": "✅ Tayyor: {topic}",
        "error": "❌ Xatolik yuz berdi: {error}",
        "restart": "Yana fayl yaratish uchun /start bosing.",
        "help": (
            "📌 Buyruqlar:\n"
            "/start - Yangi fayl yaratishni boshlash\n"
            "/history - Oldingi fayllaringiz tarixi\n"
            "/help - Yordam"
        ),
        "no_history": "Sizda hali tarix yo'q. /start bosib birinchi faylingizni yarating!",
        "history_title": "📚 Sizning fayllaringiz tarixi:\n\n",
        "btn_pptx": "📊 Slayd (PPTX)",
        "btn_docx": "📄 Mustaqil ish (DOCX)",
        "btn_pdf": "📕 PDF hujjat",
        "conclusion_title": "Xulosa",
        "conclusion_text": "Taqdimot yakunlandi. E'tiboringiz uchun rahmat!",
        "plan_title": "Reja:",
        "subtitle": "Taqdimot",
    },
    "ru": {
        "choose_lang": "Tilni tanlang / Выберите язык / Choose language:",
        "welcome": (
            "Привет! 👋\n\n"
            "Я подготовлю для вас *слайд*, *самостоятельную работу* или *PDF* файл "
            "(текст пишется с помощью AI).\n\n"
            "Какой тип файла вам нужен?"
        ),
        "ask_topic": "Напишите тему (например: 'История искусственного интеллекта'):",
        "ask_points": (
            "Теперь отправьте основные разделы/пункты.\n"
            "Каждый пункт пишите С НОВОЙ СТРОКИ.\n\n"
            "Например:\n"
            "Введение\n"
            "Основная часть\n"
            "Заключение"
        ),
        "generating": "⏳ AI пишет текст и готовит файл, подождите немного...",
        "done": "✅ Готово: {topic}",
        "error": "❌ Произошла ошибка: {error}",
        "restart": "Нажмите /start чтобы создать ещё один файл.",
        "help": (
            "📌 Команды:\n"
            "/start - Начать создание нового файла\n"
            "/history - История ваших файлов\n"
            "/help - Помощь"
        ),
        "no_history": "У вас пока нет истории. Нажмите /start чтобы создать первый файл!",
        "history_title": "📚 История ваших файлов:\n\n",
        "btn_pptx": "📊 Слайд (PPTX)",
        "btn_docx": "📄 Самостоятельная работа (DOCX)",
        "btn_pdf": "📕 PDF документ",
        "conclusion_title": "Заключение",
        "conclusion_text": "Презентация завершена. Спасибо за внимание!",
        "plan_title": "План:",
        "subtitle": "Презентация",
    },
    "en": {
        "choose_lang": "Tilni tanlang / Выберите язык / Choose language:",
        "welcome": (
            "Hello! 👋\n\n"
            "I will prepare a *slide deck*, *report* or *PDF* file for you "
            "(text is written with the help of AI).\n\n"
            "Which file type do you need?"
        ),
        "ask_topic": "Write the topic (e.g. 'History of Artificial Intelligence'):",
        "ask_points": (
            "Now send the main sections/points.\n"
            "Write each one on a NEW LINE.\n\n"
            "Example:\n"
            "Introduction\n"
            "Main part\n"
            "Conclusion"
        ),
        "generating": "⏳ AI is writing the text and preparing the file, please wait...",
        "done": "✅ Done: {topic}",
        "error": "❌ An error occurred: {error}",
        "restart": "Press /start to create another file.",
        "help": (
            "📌 Commands:\n"
            "/start - Start creating a new file\n"
            "/history - Your previous files\n"
            "/help - Help"
        ),
        "no_history": "You have no history yet. Press /start to create your first file!",
        "history_title": "📚 Your file history:\n\n",
        "btn_pptx": "📊 Slides (PPTX)",
        "btn_docx": "📄 Report (DOCX)",
        "btn_pdf": "📕 PDF document",
        "conclusion_title": "Conclusion",
        "conclusion_text": "The presentation has ended. Thank you for your attention!",
        "plan_title": "Outline:",
        "subtitle": "Presentation",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    """Berilgan til va kalit bo'yicha matnni qaytaradi."""
    lang = lang if lang in TEXTS else "uz"
    text = TEXTS[lang].get(key, TEXTS["uz"].get(key, key))
    if kwargs:
        return text.format(**kwargs)
    return text
