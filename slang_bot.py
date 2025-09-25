# slang_bot.py
import telebot
from telebot import types
import random
import logging
import os

logging.basicConfig(level=logging.INFO)

# ====== ВСТАВЬ СВОЙ ТОКЕН НИЖЕ (твой токен уже тут) ======
TOKEN = "8420284337:AAG6_0VguXPBRYyFSvDBYGRYPPdl4_bdRtw"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ====== Простая "сессия" для пользователя: режим ожидания ввода ======
# Возможные режимы: None, 'search', 'translate', 'propose'
user_state = {}         # chat_id -> mode
propose_buffer = {}     # chat_id -> raw proposal string while in propose mode

# ====== БАЗА СЛОВ (взята из твоего списка) ======
SLANG_DB = [
    {"word": "my ball", "transcription": "/maɪ bɔːl/", "ru": "моя/мой (ласково)",
     "kz": "менікі / менің (сүйіктім)", "meaning": "ласковое обращение к другу или партнёру",
     "example": "Hey my ball, wanna grab lunch?"},
    {"word": "fax, no printer", "transcription": "/fæks noʊ ˈprɪntər/", "ru": "факты, и нет принтера",
     "kz": "шын факт, принтер жоқ", "meaning": "усиленное “точно”, “реально так”",
     "example": "She hates drama - fax, no printer."},
    {"word": "gyatt", "transcription": "/dʒjæt/", "ru": "вау, круто", "kz": "керемет / таңғаларлық",
     "meaning": "комплимент, часто по поводу тела или обаяния", "example": "Bro, that fit is gyatt."},
    {"word": "skibidi", "transcription": "/ˌskiːˈbiːdi/", "ru": "мемное слово, “странно/весело”",
     "kz": "күлкілі / таңқаларлық", "meaning": "выражение необычного или абсурдного",
     "example": "The whole party vibe was so skibidi."},
    {"word": "Ohio", "transcription": "/oʊˈhaɪˌoʊ/", "ru": "что-то абсурдное / странное",
     "kz": "абсурд / оғаш", "meaning": "описывает что-то нелогичное, неподобающее",
     "example": "Bro just jumped in, screaming. Ohio."},
    {"word": "rizz", "transcription": "/rɪz/", "ru": "харизма, обаяние", "kz": "харизма / тартымдылық",
     "meaning": "умение обворожить, флиртовать", "example": "He’s got so much rizz."},
    {"word": "delulu", "transcription": "/dɪˈluːluː/", "ru": "живёт в иллюзиях", "kz": "қиялға берілген",
     "meaning": "когда человек фантазирует, не признаёт реальность", "example": "Stop being delulu, she didn’t even text back."},
    {"word": "fanum tax", "transcription": "/fæˈnʌm tæks/", "ru": "“налог” за фанатство",
     "kz": "фанат болу салығы", "meaning": "шутка о том, сколько внимания нужно вложить, чтобы быть “фанатом”",
     "example": "If you stan that group, the fanum tax is real."},
    {"word": "touch grass", "transcription": "/tʌtʃ ɡræs/", "ru": "“отойди от экрана”",
     "kz": "далаға шық / далада дем ал", "meaning": "рекомендация выйти из сети", "example": "You need to touch grass, been gaming 10 hrs."},
    {"word": "mid", "transcription": "/mɪd/", "ru": "посредственно", "kz": "орташа / көңілсіз",
     "meaning": "что-то среднее, не впечатляет", "example": "That song was mid."},
    {"word": "no simp", "transcription": "/noʊ sɪmp/", "ru": "не быть “симпом”", "kz": "симп болмау",
     "meaning": "чрезмерно ухаживать или восхищаться кем-то без ответной реакции", "example": "Quit simping for someone who doesn’t care."},
    {"word": "simping", "transcription": "/ˈsɪmpɪŋ/", "ru": "симпить", "kz": "симп жасау", "meaning": "см. no simp", "example": ""},
    {"word": "skrrt skrrt", "transcription": "/skɜːrt skɜːrt/", "ru": "“у-ух”, звук “уезжаю”",
     "kz": "жылдам кету / дыбыс эффекті", "meaning": "мемная фраза / звук", "example": "He saw his ex, skrrt skrrt outta the room."},
    {"word": "girl dinner", "transcription": "/gɜːrl ˈdɪnər/", "ru": "“ужин девушки” (перекусы)",
     "kz": "қыз кешкі асы / жеңіл кешкі ас", "meaning": "ужин из перекусов", "example": "Tonight’s girl dinner = chips + pickles."},
    {"word": "boy dinner", "transcription": "/bɔɪ ˈdɪnər/", "ru": "“ужин парня”", "kz": "жігіт кешкі асы",
     "meaning": "аналогично “girl dinner”", "example": "Boy dinner: chicken tenders and soda."},
    {"word": "mood flex", "transcription": "/muːd flɛks/", "ru": "показать настроение / эстетику", "kz": "көңіл-күй көрсету",
     "meaning": "демонстрация эстетики или настроения", "example": "Her page is full moodboard flex."},
    {"word": "moodboard flex", "transcription": "/ˈmuːdbɔːrd flɛks/", "ru": "вариант mood flex", "kz": "",
     "meaning": "см. mood flex", "example": ""},
    {"word": "oka", "transcription": "/oʊkə/", "ru": "усиленное “окей”", "kz": "жарайды", "meaning": "эмоциональное “окей”",
     "example": "You got it? Okurr!"},
    {"word": "okurr", "transcription": "/oʊˈkʌr(r)/", "ru": "вариант okurr", "kz": "", "meaning": "см. oka", "example": ""},
    {"word": "glow down", "transcription": "/ɡloʊ daʊn/", "ru": "падение после “glow up”", "kz": "кері жарқырау",
     "meaning": "ухудшение после периода улучшения", "example": "Since moving off campus, she’s had a glow down."},
    {"word": "ded", "transcription": "/dɛd/", "ru": "умер(от смеха)", "kz": "күлден өлдім",
     "meaning": "сильное выражение реакции", "example": "That joke? I’m ded."},
    {"word": "I'm ded", "transcription": "/aɪm dɛd/", "ru": "я умер(от смеха)", "kz": "күлуден өлдім", "meaning": "см. ded", "example": ""},
    {"word": "ratio'ed", "transcription": "/ˈreɪʃi.oʊd/", "ru": "больше ответов, чем оригинала",
     "kz": "жауаптардың көп болуы", "meaning": "когда оригинал теряет поддержку в комментариях", "example": "Bro’s tweet got ratio’ed instantly."},
    {"word": "ratio", "transcription": "/ˈreɪʃi.oʊ/", "ru": "ratio (сущ.)", "kz": "", "meaning": "см. ratio'ed", "example": ""},
    {"word": "main character energy", "transcription": "/meɪn ˈkærɪktər ˈɛnərdʒi/",
     "ru": "быть главным героем", "kz": "басты кейіпкер сияқтанып жүру",
     "meaning": "жить как будто ты — центр внимания", "example": "Walking into work like I got main character energy."},
    {"word": "chefs kiss", "transcription": "/ʧɛfs kɪs/", "ru": "идеальное, “мастер-поцелуй”",
     "kz": "мінсіз", "meaning": "что-то идеально выполнено", "example": "Her makeup? Chefs kiss."},
    {"word": "pog", "transcription": "/pɔg/", "ru": "круто", "kz": "керемет", "meaning": "реакция на что-то классное",
     "example": "That goal was poggers!"},
    {"word": "poggers", "transcription": "/ˈpɔgərz/", "ru": "вариант pog", "kz": "", "meaning": "см. pog", "example": ""},
    {"word": "based", "transcription": "/beɪst/", "ru": "искренний, твёрд в своих взглядах",
     "kz": "негізі бар", "meaning": "восхищение честностью или стойкостью мнения", "example": "That stand you took, based."},
    {"word": "sus", "transcription": "/sʌs/", "ru": "подозрительный / странный", "kz": "күмәнді / оғаш",
     "meaning": "что-то вызывает сомнения", "example": "Everything she says sounds sus."},
    {"word": "shooketh", "transcription": "/ˈʃuːkɛθ/", "ru": "сильно шокирован / удивлён", "kz": "қатты таңғалдым",
     "meaning": "гиперболизированное “я шокирован”", "example": "You saw her price tag? I’m shooketh."},
    {"word": "rent free", "transcription": "/rɛnt friː/", "ru": "“живёт в голове бесплатно”",
     "kz": "ойымда ақысыз тұр", "meaning": "когда что-то постоянно думается о тебе", "example": "That line from the movie is living rent free in my head."},
    {"word": "crumbing", "transcription": "/ˈkrʌmɪŋ/", "ru": "“крошки внимания”", "kz": "үміт-крошкалар",
     "meaning": "давать маленькие знаки внимания, не развивая отношения", "example": "He’s just crumbing, he never commits."},
    {"word": "orbiting", "transcription": "/ˈɔːrbɪtɪŋ/", "ru": "быть “в орбите”", "kz": "орбитада болу",
     "meaning": "поддерживать минимальный контакт через лайки/сторис", "example": "Since we broke up, she’s still orbiting me."},
    {"word": "drip check", "transcription": "/drɪp ʧɛk/", "ru": "проверка стиля / образа", "kz": "стиль сынау",
     "meaning": "показать или оценить наряд / внешний вид", "example": "Post your drip check, let’s see."},
    {"word": "simp tax", "transcription": "/sɪmp tæks/", "ru": "“налог симпинга”", "kz": "симпинг салығы",
     "meaning": "сколько нужно вложить, если быть симпом", "example": "That gift? High simp tax."},
    {"word": "bussin’", "transcription": "/ˈbʌsɪn/", "ru": "очень вкусно / очень круто", "kz": "дәмді",
     "meaning": "используется к еде или когда что-то особенно приятное", "example": "Those tacos? Bussin’."},
    {"word": "eat the beat", "transcription": "/iːt ðə biːt/", "ru": "“съесть бит”", "kz": "әуенді сезу",
     "meaning": "прочувствовать музыку, «вырваться» на сцене", "example": "DJ dropped the track, we eat the beat."},
    {"word": "psy-check", "transcription": "/saɪ ʧɛk/", "ru": "проверка состояния / настроения", "kz": "көңіл-күйді тексеру",
     "meaning": "спрашивают, как человек себя ощущает", "example": "Mood check: who’s staying home tonight?"},
    {"word": "mood check", "transcription": "/muːd ʧɛk/", "ru": "вариант", "kz": "", "meaning": "см. psy-check", "example": ""},
    {"word": "yikes no", "transcription": "/jaɪks noʊ/", "ru": "“ой, нет / ужс-нет”", "kz": "ай, жоқ",
     "meaning": "реакция на что-то неприятное", "example": "They asked me- that? Yikes no."},
    {"word": "sussy baka remix", "transcription": "/ˈsʌsi ˈbɑːkə rɪˈmɪks/", "ru": "“подозрительный дурак ремикс”",
     "kz": "күмәнді ақымақ ремикс", "meaning": "комбинация мемов и шуток", "example": "This video is the sussy baka remix we needed."},
    {"word": "ghost texting", "transcription": "/goʊst ˈtɛkstɪŋ/", "ru": "“привидеть - писать”",
     "kz": "хабарлама арқылы “жалғандық” жасау", "meaning": "отправлять сообщения, но не продолжать разговор", "example": "After last night, he ghost texts me."},
    {"word": "caspering", "transcription": "/ˈkæspərɪŋ/", "ru": "мягкий ghosting / уход полумерами",
     "kz": "жұмсақ қатысу", "meaning": "не отвечает полностью, но и не блокирует", "example": "She didn’t block him, she’s just caspering."},
    {"word": "literal-ly", "transcription": "/ˈlɪtərəlli/", "ru": "буквально / иронично",
     "kz": "сөзбе-сөз (ирониямен)", "meaning": "использование 'literally' ради усиления", "example": "I’m literally dying laughing."},
    {"word": "softboy", "transcription": "/sɔft bɔɪ/", "ru": "мягкий стиль", "kz": "жұмсақ стиль",
     "meaning": "мягкий/уютный стиль поведения и внешности", "example": "Her room decor is so softgirl aesthetic."},
    {"word": "softgirl aesthetic", "transcription": "/sɔft gɜːrl æsˈθɛtɪk/", "ru": "мягкая эстетика", "kz": "",
     "meaning": "см. softboy", "example": ""},
    {"word": "beam", "transcription": "/biːm/", "ru": "сиять / лучить", "kz": "жарқырау",
     "meaning": "когда кто-то выглядит очень ярко", "example": "She just beam walking into class."},
    {"word": "zeus mode", "transcription": "/zjuːs moʊd/", "ru": "режим Зевса", "kz": "Зевс режимі",
     "meaning": "ощущение максимальной уверенности", "example": "After winning that match, I’m on Zeus mode."},
    {"word": "lost cap", "transcription": "/lɒst kæp/", "ru": "потерял 'шляпу' / ошибся", "kz": "кепка жоғалды",
     "meaning": "вариант 'no cap', когда признаёшь ошибку", "example": "I thought I’d win, lost cap on that."},
    {"word": "scroll sad", "transcription": "/skroʊl sæd/", "ru": "грусть от постоянного скролла", "kz": "",
     "meaning": "когда долго сидишь в соцсетях и грустишь", "example": "Scrolled for hours, now I’m scroll sad."},
    {"word": "fit check", "transcription": "/fɪt ʧɛk/", "ru": "проверка аутфита", "kz": "киім тексеру",
     "meaning": "показать свой наряд / смотреть, что на других", "example": "Fit check before we leave."},
    {"word": "rage quit", "transcription": "/reɪʤ kwɪt/", "ru": "выйти в гневе / бросить", "kz": "ашумен кету",
     "meaning": "когда бросаешь что-то из раздражения", "example": "I can’t deal with lag, rage quit."},
    {"word": "vibe shift", "transcription": "/vaɪb ʃɪft/", "ru": "смена вайба / настроения", "kz": "атмосфераның өзгеруі",
     "meaning": "изменение настроения в компании / соцсетях", "example": "We went from jokes to serious real quick — vibe shift."},
]

# ====== ХЕЛПЕРЫ ======
def format_entry(entry: dict) -> str:
    return (
        f"<b>{entry.get('word','—')}</b> {entry.get('transcription','')}\n"
        f"Перевод (RU): {entry.get('ru','—')}\n"
        f"Перевод (KZ): {entry.get('kz','—')}\n"
        f"Значение: {entry.get('meaning','—')}\n"
        f"Пример: {entry.get('example','—')}"
    )

def normalize(s: str) -> str:
    return "".join(s.lower().split())  # удаляем пробелы, переводим в lower

def find_in_db(query: str):
    q = query.strip().lower()
    q_norm = normalize(query)
    exact = []
    partial = []
    for e in SLANG_DB:
        w = e['word'].lower()
        w_norm = normalize(e['word'])
        if w == q or w_norm == q_norm:
            exact.append(e)
        elif q in w or w in q or q_norm == w_norm:
            partial.append(e)
        elif q in w.replace('-', ' ') or q in w.replace(' ', ''):
            partial.append(e)
    # exact first, then partial
    return exact + partial

# ====== INLINE-MENU ======
def send_main_menu(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎲 Random", callback_data="random"),
               types.InlineKeyboardButton("🔎 Поиск", callback_data="search"))
    markup.add(types.InlineKeyboardButton("✍️ Предложить слово", callback_data="suggest"),
               types.InlineKeyboardButton("🌐 Переводчик", callback_data="translate"))
    bot.send_message(chat_id, "Привет! Я Slang Buddy — твой помощник по современному английскому сленгу.\n\nВыбери действие 👇", reply_markup=markup)

# ====== HANDLERS ======
@bot.message_handler(commands=['start'])
def cmd_start(message):
    user_state.pop(message.chat.id, None)
    send_main_menu(message.chat.id)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call: types.CallbackQuery):
    cid = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)  # убирает "крутилку"
    user_state[cid] = None  # сброс режима по умолчанию

    if data == "random":
        entry = random.choice(SLANG_DB)
        bot.send_message(cid, "🎲 Random: " + format_entry(entry))
    elif data == "search":
        user_state[cid] = 'search'
        bot.send_message(cid, "🔎 Введи слово или фразу для поиска (например: vibe shift):")
    elif data == "translate":
        user_state[cid] = 'translate'
        bot.send_message(cid, "🌐 Введи текст на английском для перевода (авто) — пытаемся через deep-translator, если установлен.")
    elif data == "suggest":
        user_state[cid] = 'propose'
        bot.send_message(cid, "✍️ Предложи слово для добавления.\nФормат: word | transcription | translation_ru | translation_kz | meaning | example\n(всё в одной строке, разделитель — вертикальная черта `|`)")

@bot.message_handler(func=lambda m: True)
def handle_text(message: types.Message):
    cid = message.chat.id
    text = message.text.strip()
    mode = user_state.get(cid)

    # Если мы в режиме поиска:
    if mode == 'search':
        results = find_in_db(text)
        if results:
            # отправляем несколько результатов (до 5)
            for r in results[:5]:
                bot.send_message(cid, format_entry(r))
        else:
            # нет результатов
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("✍️ Предложить добавить это слово", callback_data="suggest"))
            bot.send_message(cid, "Ничего не найдено в базе. Хотите предложить это слово для модерации?", reply_markup=markup)
        user_state[cid] = None
        return

    # Если в режиме переводчика:
    if mode == 'translate':
        # пытаемся использовать deep-translator если установлен
        try:
            from deep_translator import GoogleTranslator
            tr = GoogleTranslator(source='auto', target='ru').translate(text)
            bot.send_message(cid, f"🔁 Перевод (en → ru):\n{tr}")
        except Exception as e:
            logging.exception("translate error")
            bot.send_message(cid, "Не удалось выполнить автоматический перевод (модуль 'deep-translator' не установлен или ошибка).")
        user_state[cid] = None
        return

    # Если в режиме предложения:
    if mode == 'propose':
        # ожидаем формат в одну строку: word | transcription | ru | kz | meaning | example
        parts = [p.strip() for p in text.split("|")]
        if len(parts) < 1:
            bot.send_message(cid, "Формат неправильный. Оставь: word | transcription | ru | kz | meaning | example")
            return
        # нормализуем коротко и сохраняем
        while len(parts) < 6:
            parts.append("")
        row = "\t".join(parts)
        try:
            with open("proposals.txt", "a", encoding="utf-8") as f:
                f.write(row + "\n")
            bot.send_message(cid, "Спасибо! Твоё предложение сохранено и будет проверено модератором.")
        except Exception as e:
            logging.exception("save proposal")
            bot.send_message(cid, "Ошибка при сохранении предложения. Попробуй позже.")
        user_state[cid] = None
        return

    # Если нет специального режима — просто попробуем найти слово по базе автоматически:
    results = find_in_db(text)
    if results:
        for r in results[:5]:
            bot.send_message(cid, format_entry(r))
    else:
        # ничего не найдено — предложим вариант добавить
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔎 Искать (режим)", callback_data="search"),
                   types.InlineKeyboardButton("✍️ Предложить слово", callback_data="suggest"))
        bot.send_message(cid, "Не нашёл в базе. Можешь: перейти в режим поиска или предложить слово на добавление.", reply_markup=markup)

# ====== ЗАПУСК ======
if __name__ == "__main__":
    print("Bot starting...")
    bot.infinity_polling()
