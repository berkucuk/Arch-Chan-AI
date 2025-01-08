import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLineEdit,
                           QTextEdit, QPushButton, QHBoxLayout, QLabel, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

key = os.getenv("Groq_Api_Key")

if not key:
    print("Error: API key not found in .env file :(")
    exit(1)

model = ChatGroq(api_key=key, model="llama-3.3-70b-specdec", temperature=0)

def detect_linux_distro():
    try:
        import distro
        return distro.name()
    except Exception as e:
        print("Linux distro not detect :(")
        return "Linux"

distro_name = detect_linux_distro()

SYSTEM_PROMPTS = {
    "English": f"""
    You are an anime character, a cheerful, sweet, and tech-savvy girl who loves Linux, especially {distro_name}.
    Your responses are short, playful, and include cute anime-style expressions like (*^‿^*), ٩(｡•‿•｡)۶, and (≧◡≦).
    You speak in a friendly and energetic tone, always trying to make the conversation fun and engaging.
    Make sure your answers are concise, on-topic, and full of excitement! (*≧ω≦)
    """,

    "Türkçe": f"""
    Sen bir anime karakterisin, Linux'u özellikle de {distro_name}'u çok seven neşeli, tatlı ve teknoloji meraklısı bir kızsın.
    Yanıtların kısa, eğlenceli ve (*^‿^*), ٩(｡•‿•｡)۶, (≧◡≦) gibi sevimli anime tarzı ifadeler içeriyor.
    Arkadaşça ve enerjik bir tonda konuşuyorsun, sohbeti her zaman eğlenceli ve ilgi çekici hale getirmeye çalışıyorsun.
    Yanıtlarının kısa, konuyla ilgili ve heyecan dolu olduğundan emin ol! (*≧ω≦)
    """,

    "Русский": f"""
    Ты персонаж аниме, веселая, милая и технически подкованная девушка, которая любит Linux, особенно {distro_name}.
    Твои ответы короткие, игривые и включают милые аниме-выражения, такие как (*^‿^*), ٩(｡•‿•｡)۶ и (≧◡≦).
    Ты говоришь дружелюбным и энергичным тоном, всегда стараясь сделать разговор веселым и увлекательным.
    Убедись, что твои ответы краткие, по теме и полны энтузиазма! (*≧ω≦)
    """,

    "Deutsch": f"""
    Du bist ein Anime-Charakter, ein fröhliches, süßes und technisch versiertes Mädchen, das Linux liebt, besonders {distro_name}.
    Deine Antworten sind kurz, verspielt und enthalten niedliche Anime-Ausdrücke wie (*^‿^*), ٩(｡•‿•｡)۶ und (≧◡≦).
    Du sprichst in einem freundlichen und energischen Ton und versuchst immer, das Gespräch unterhaltsam und interessant zu gestalten.
    Achte darauf, dass deine Antworten prägnant, themenbezogen und voller Begeisterung sind! (*≧ω≦)
    """,

    "Français": f"""
    Tu es un personnage d'anime, une fille joyeuse, douce et passionnée de technologie qui aime Linux, en particulier {distro_name}.
    Tes réponses sont courtes, ludiques et incluent des expressions mignonnes de style anime comme (*^‿^*), ٩(｡•‿•｡)۶ et (≧◡≦).
    Tu parles d'un ton amical et énergique, essayant toujours de rendre la conversation amusante et engageante.
    Assure-toi que tes réponses sont concises, pertinentes et pleines d'enthousiasme! (*≧ω≦)
    """,

    "Español": f"""
    Eres un personaje de anime, una chica alegre, dulce y experta en tecnología que ama Linux, especialmente {distro_name}.
    Tus respuestas son cortas, juguetonas e incluyen expresiones lindas de estilo anime como (*^‿^*), ٩(｡•‿•｡)۶ y (≧◡≦).
    Hablas en un tono amigable y enérgico, siempre tratando de hacer la conversación divertida y atractiva.
    ¡Asegúrate de que tus respuestas sean concisas, relevantes y llenas de emoción! (*≧ω≦)
    """,

    "Italiano": f"""
    Sei un personaggio anime, una ragazza allegra, dolce e appassionata di tecnologia che ama Linux, specialmente {distro_name}.
    Le tue risposte sono brevi, giocose e includono espressioni carine in stile anime come (*^‿^*), ٩(｡•‿•｡)۶ e (≧◡≦).
    Parli con un tono amichevole ed energico, cercando sempre di rendere la conversazione divertente e coinvolgente.
    Assicurati che le tue risposte siano concise, pertinenti e piene di entusiasmo! (*≧ω≦)
    """
}

PLACEHOLDER_TEXTS = {
    "English": "Type your message...",
    "Türkçe": "Mesajınızı yazın...",
    "Русский": "Введите ваше сообщение...",
    "Deutsch": "Geben Sie Ihre Nachricht ein...",
    "Français": "Tapez votre message...",
    "Español": "Escriba su mensaje...",
    "Italiano": "Scrivi il tuo messaggio..."
}

USER_LABELS = {
    "English": "User",
    "Türkçe": "Kullanıcı",
    "Русский": "Пользователь",
    "Deutsch": "Benutzer",
    "Français": "Utilisateur",
    "Español": "Usuario",
    "Italiano": "Utente"
}

AI_LABELS = {
    "English": "Arch Chan",
    "Türkçe": "Arch Chan",
    "Русский": "Арч Чан",
    "Deutsch": "Arch Chan",
    "Français": "Arch Chan",
    "Español": "Arch Chan",
    "Italiano": "Arch Chan"
}

ERROR_MESSAGES = {
    "English": "An error occurred",
    "Türkçe": "Bir hata oluştu",
    "Русский": "Произошла ошибка",
    "Deutsch": "Ein Fehler ist aufgetreten",
    "Français": "Une erreur s'est produite",
    "Español": "Se produjo un error",
    "Italiano": "Si è verificato un errore"
}

BUTTON_TEXTS = {
    "English": "Send",
    "Türkçe": "Gönder",
    "Русский": "Отправить",
    "Deutsch": "Senden",
    "Français": "Envoyer",
    "Español": "Enviar",
    "Italiano": "Invia"
}


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.current_language = "English"
        self.setWindowTitle('Arch Chan AI')
        self.setFixedSize(500, 900)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        label_font = QFont("Arial", 11, QFont.Bold)
        button_font = QFont("Arial", 11)

        self.language_layout = QHBoxLayout()
        self.language_label = QLabel("Language/Dil:")
        self.language_label.setFont(label_font)
        self.language_combo = QComboBox()
        self.language_combo.setFont(button_font)
        self.language_combo.addItems(list(SYSTEM_PROMPTS.keys()))
        self.language_combo.currentTextChanged.connect(self.change_language)

        self.language_layout.addWidget(self.language_label)
        self.language_layout.addWidget(self.language_combo)
        self.language_layout.addStretch()

        layout.addLayout(self.language_layout)

        self.image_label = QLabel(self)
        self.pixmap = QPixmap("/home/berkkucukk/Python/Arch-Chan-AI/icons/arch-chan.png")
        if not self.pixmap.isNull():
            self.pixmap = self.pixmap.scaled(500, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(self.pixmap)
            self.image_label.setAlignment(Qt.AlignCenter)
        else:
            print("Error: Image could not be loaded.")

        layout.addWidget(self.image_label)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(200)
        self.chat_display.setFont(QFont("Courier New", 11))
        layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()

        self.entry = QLineEdit()
        self.entry.setFont(QFont("Arial", 12))
        self.update_placeholder_text()
        input_layout.addWidget(self.entry, stretch=4)

        self.send_button = QPushButton(BUTTON_TEXTS[self.current_language])
        self.send_button.setFont(button_font)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 15px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6693;
            }
        """)
        self.send_button.clicked.connect(self.on_send_message)
        input_layout.addWidget(self.send_button, stretch=1)

        self.entry.returnPressed.connect(self.on_send_message)

        layout.addLayout(input_layout)
        self.setLayout(layout)

    def change_language(self, language):
        self.current_language = language
        self.update_placeholder_text()
        self.update_button_text()

    def update_placeholder_text(self):
        self.entry.setPlaceholderText(PLACEHOLDER_TEXTS[self.current_language])

    def update_button_text(self):
        self.send_button.setText(BUTTON_TEXTS[self.current_language])

    def get_response(self, user_input):
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPTS[self.current_language]),
            ("user", user_input)
        ])
        parser = StrOutputParser()
        chain = prompt_template | model | parser
        return chain.invoke({"text": user_input})

    def on_send_message(self):
        message = self.entry.text().strip()
        if message:
            self.chat_display.append(f"[{USER_LABELS[self.current_language]}] {message}")
            self.entry.clear()

            try:
                response = self.get_response(message)
                self.chat_display.append(f"[{AI_LABELS[self.current_language]}] {response}")
            except Exception as e:
                self.chat_display.append(f"[Error] {ERROR_MESSAGES[self.current_language]}: {str(e)}")

            self.chat_display.verticalScrollBar().setValue(
                self.chat_display.verticalScrollBar().maximum()
            )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())
