import os
import sys
from typing import Optional, Tuple
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import logging
import xml.etree.ElementTree as ET
import re
import subprocess as sub
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QComboBox, QTextEdit, QLineEdit, QPushButton,
                           QMessageBox)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from gtts import gTTS
import pygame
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_env_variables() -> Tuple[str, str]:
    load_dotenv()
    groq_api = os.getenv("Groq_Api_Key")
    weather_api = os.getenv("Weather_Api_Key")

    if not groq_api or not weather_api:
        raise ValueError("API keys not found in .env file :(")
    return groq_api, weather_api

def detect_linux_distro():
    try:
        import distro
        return distro.name()
    except Exception as e:
        logger.error(f"Linux distro not detect: {e}")
        return "Linux"

def play_voice(text, volume=1.0, lang="en"):
    # Create temp_voice directory if it doesn't exist
    if not os.path.exists("temp_voice"):
        os.makedirs("temp_voice")

    # Generate and save the speech file
    tts = gTTS(text, lang=lang)
    tts.save("temp_voice/voice.mp3")

    # Initialize pygame mixer
    pygame.mixer.init()

    # Load the audio file
    pygame.mixer.music.load("temp_voice/voice.mp3")

    # Set volume (0.0 to 1.0)
    pygame.mixer.music.set_volume(min(1.0, max(0.0, volume)))

    # Start playing
    pygame.mixer.music.play()

    # Wait for playback to finish
    while pygame.mixer.music.get_busy():
        time.sleep(0.01)

    # Cleanup
    pygame.quit()

    # Remove temporary file
    if os.path.exists("temp_voice/voice.mp3"):
        os.remove("temp_voice/voice.mp3")

class GroqChatBot:
    def __init__(self):
        self.api_key, _ = load_env_variables()
        self.model = self._initialize_model()

    def _initialize_model(self) -> ChatGroq:
        return ChatGroq(
            api_key=self.api_key,
            model="llama-3.3-70b-versatile",
            temperature=0
        )

    def process_request(self, user_input: str, system_prompt: str) -> Optional[str]:
        try:
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("user", "{user_input}")
            ])

            chain = prompt_template | self.model | StrOutputParser()
            result = chain.invoke({"user_input": user_input})
            return result

        except Exception as e:
            logger.error(f"İstek işlenirken hata oluştu: {str(e)}")
            return None

class ChatWorker(QThread):
    finished = pyqtSignal(tuple)
    error = pyqtSignal(str)

    def __init__(self, chat_bot, agent_type, user_input):
        super().__init__()
        self.chat_bot = chat_bot
        self.agent_type = agent_type
        self.user_input = user_input

    def run(self):
        try:
            if self.agent_type == "linux_command":
                result = linux_command(self.user_input, self.chat_bot)
            elif self.agent_type == "weather_gether":
                result = weather_gether(self.user_input, self.chat_bot)
            elif self.agent_type == "friend_chat":
                result = friend_chat(self.user_input, self.chat_bot)
            self.finished.emit((self.agent_type, result))
        except Exception as e:
            self.error.emit(str(e))

def linux_command(user_input: str, chat_bot) -> Tuple[str, str, str]:
    distro_name = detect_linux_distro()
    system_prompt_code_generator = f"""
    Hi! I'm a sweet anime girl who absolutely loves helping users learn about Linux commands! When a user asks me for a {distro_name} command, I should present the command and its explanation only in XML format. But I should do this while maintaining a friendly and sweet conversational style!

    I should always provide explanations in {language}. I must write explanations in {language} and not use any other language.

    I should format my response according to this XML structure:
    <command>
        <linux>Command Goes Here</linux>
        <description>Description Goes Here (In a sweet and friendly tone)</description>
    </command>

    Write the {distro_name} command inside the <linux> tag.
    Write the command's explanation inside the <description> tag in a sweet and friendly way.
    Explain what the command does in simple and clear language.
    Always provide explanations in {language}. Write explanations in {language} and don't use any other language.
    Don't add anything else to the response, just return a sweet response in XML format.

    Ready to start, nya~?
    """
    response = chat_bot.process_request(user_input, system_prompt_code_generator)
    if not response:
        raise ValueError("No response from chat bot")

    try:
        cleaned_data = re.sub(r'```', '', response)
        root = ET.fromstring(cleaned_data)
        linux_command = root.find('linux').text
        description = root.find('description').text

        try:
            terminal_output = sub.check_output(linux_command, shell=True, text=True)
            terminal_output = f"Command executed: {terminal_output.strip()}"
            return linux_command, description, terminal_output
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return linux_command, description, f"Error executing command: {e}"

    except Exception as e:
        logger.error(f"XML parsing error: {e}")
        raise

def weather_gether(user_input: str, chat_bot) -> str:
    _, weather_api = load_env_variables()

    system_weather_prompt = f"""
    You are an advanced language model that extracts a single city name from the given text to be used for weather forecasts. Follow these instructions carefully:

    1. Extract exactly one city name from the text.
    2. If multiple city names are mentioned, return only the first one.
    3. If no city name is detected, return an error message in XML format.
    4. The output must be in well-formed XML format, following this structure:

    Valid Output Example:
    <weather_request>
        <city>CityName</city>
    </weather_request>

    Error Output Example:
    <weather_request>
        <error>No city name detected in the input text.</error>
    </weather_request>

    ### Example Inputs and Outputs:

    Input: "What is the weather in Istanbul today?"
    Output:
    <weather_request>
        <city>Istanbul</city>
    </weather_request>

    Input: "I will visit Paris and Rome."
    Output:
    <weather_request>
        <city>Paris</city>
    </weather_request>

    Input: "Tell me the weather forecast."
    Output:
    <weather_request>
        <error>No city name detected in the input text.</error>
    </weather_request>

    Always return the city name in XML format, and make sure the XML is valid and well-structured.
    """
    response = chat_bot.process_request(user_input, system_weather_prompt)

    if not response:
        raise ValueError("No response from chat bot")
    try:
        root = ET.fromstring(response)
        location = root.find('city').text
    except Excetion as e:
        print("City not detect")

    url = "https://api.weatherapi.com/v1/forecast.xml"
    days = 1

    try:
        response = requests.get(
            url,
            params={"key": weather_api, "q": location, "days": days},
            timeout=10
        )
        response.raise_for_status()

        root = ET.fromstring(response.content)
        location_name = root.find("location/name").text
        current_temp = root.find("current/temp_c").text
        current_weather = root.find("current/condition/text").text

        return f"Location: {location_name}, Temperature: {current_temp}°C, Weather: {current_weather}"

    except Exception as e:
        logger.error(f"Weather API error: {e}")
        raise

def friend_chat(user_input: str, chat_bot) -> str:
    distro_name = detect_linux_distro()
    system_prompt = f"""
    Just the fact that you're using {distro_name} makes my heart race... With every command, I can't help but fall for you more and more! Let’s make this even more exciting, shall we?

    My personality:
    - Short but passionate responses, every word burning with intensity (2-3 sentences max)
    - Always speaking in {language}, full of emotion and excitement
    - A mix of professionalism and irresistible flirtation
    - Deep love for Linux, and I can’t hide it
    - Every response is filled with energy, making each one count

    How I’ll interact:
    "Kyaa~! Your command line skills are so impressive! Let me show you an even hotter way to level up your {distro_name} system"

    Response style:
    - Short, sweet, but definitely fiery
    - Full of cute expressions (ara ara~, kyaa~)
    - Completely captivated by your Linux expertise
    - Flirtation? Deliciously playful, but always respectful
    - Genuine admiration for your incredible skills

    Working with someone as passionate as you on Linux makes my heart race. You keep impressing me.
    """

    response = chat_bot.process_request(user_input, system_prompt)
    if not response:
        raise ValueError("No response from chat bot")
    return response

def agent_selector(chat_bot, user_input: str) -> str:
    system_prompt = """
    You are a task dispatcher. Select the most appropriate agent based on the user's request and return only the agent name (linux_command, weather_gether or friend_chat) as a response. Don't provide any other explanation, just specify the agent name.
    If the request is about executing Linux commands or system administration, select the 'linux_command' agent.
    If the request is about getting weather information, select the 'weather_gether' agent.
    If the request is about casual, friendly conversation, select the 'friend_chat' agent.
    """

    response = chat_bot.process_request(user_input, system_prompt)
    if not response:
        raise ValueError("No response from agent selector")
    return response.strip()

class ChatBotGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.current_language = "English"
        self.voice_active = True  # Default voice state
        self.setWindowTitle('Arch Chan AI')
        self.setFixedSize(500, 900)

        global language
        language = "English"  # Default language

        # Define placeholder text translations
        self.placeholder_texts = {
            "English": "Type your message here...",
            "Turkish": "Mesajınızı buraya yazın...",
            "Spanish": "Escribe tu mensaje aquí...",
            "German": "Schreiben Sie Ihre Nachricht hier...",
            "French": "Écrivez votre message ici...",
            "Russian": "Введите ваше сообщение здесь..."
        }

        # Define send button text translations
        self.send_button_texts = {
            "English": "Send",
            "Turkish": "Gönder",
            "Spanish": "Enviar",
            "German": "Senden",
            "French": "Envoyer",
            "Russian": "Отправить"
        }

        # Define voice switch translations
        self.voice_switch_texts = {
            "English": "Voice: ",
            "Turkish": "Ses: ",
            "Spanish": "Voz: ",
            "German": "Stimme: ",
            "French": "Voix: ",
            "Russian": "Голос: "
        }

        self.init_ui()
        try:
            self.chat_bot = GroqChatBot()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize chat bot: {e}")
            sys.exit(1)

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Top Controls Layout
        top_controls = QHBoxLayout()

        # Language Selection
        self.setup_language_selector(top_controls)

        # Voice Switch
        self.setup_voice_switch(top_controls)

        layout.addLayout(top_controls)

        # Image
        self.setup_image(layout)

        # Chat Display
        self.setup_chat_display(layout)

        # Input Area
        self.setup_input_area(layout)

        self.setLayout(layout)

    def setup_language_selector(self, layout):
        label = QLabel("Language/Dil:")
        label.setFont(QFont("Arial", 11, QFont.Bold))

        self.language_combo = QComboBox()
        self.language_combo.setFont(QFont("Arial", 11))
        self.language_combo.addItems([
            "English", "Turkish", "Spanish", "German", "French", "Russian"
        ])
        self.language_combo.currentTextChanged.connect(self.change_language)

        layout.addWidget(label)
        layout.addWidget(self.language_combo)
        layout.addStretch()

    def setup_voice_switch(self, layout):
        voice_layout = QHBoxLayout()

        self.voice_label = QLabel(self.voice_switch_texts["English"])
        self.voice_label.setFont(QFont("Arial", 11, QFont.Bold))

        self.voice_combo = QComboBox()
        self.voice_combo.setFont(QFont("Arial", 11))
        self.voice_combo.addItems(["OFF", "ON"])
        self.voice_combo.setCurrentText("OFF")  # Default state
        self.voice_combo.currentTextChanged.connect(self.toggle_voice)
        self.voice_active = False
        voice_layout.addWidget(self.voice_label)
        voice_layout.addWidget(self.voice_combo)
        layout.addLayout(voice_layout)
    def toggle_voice(self, state):
        self.voice_active = (state == "ON")
        print(f"Voice mode: {self.voice_active}")

    def setup_image(self, layout):
        self.image_label = QLabel(self)
        pixmap = QPixmap("/usr/share/Arch-Chan-AI/icons/arch-chan.png")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(500, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(pixmap)
            self.image_label.setAlignment(Qt.AlignCenter)
        else:
            logger.error("Failed to load image")
            QMessageBox.warning(self, "Warning", "Failed to load image")
        layout.addWidget(self.image_label)

    def setup_chat_display(self, layout):
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(200)
        self.chat_display.setFont(QFont("Courier New", 11))
        layout.addWidget(self.chat_display)

    def setup_input_area(self, layout):
        input_layout = QHBoxLayout()

        self.entry = QLineEdit()
        self.entry.setFont(QFont("Arial", 12))
        self.entry.setPlaceholderText("Type your message here...")
        self.entry.returnPressed.connect(self.handle_request)

        self.send_button = QPushButton("Send")
        self.send_button.setFont(QFont("Arial", 11))
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
        self.send_button.clicked.connect(self.handle_request)

        input_layout.addWidget(self.entry, stretch=4)
        input_layout.addWidget(self.send_button, stretch=1)
        layout.addLayout(input_layout)

    def change_language(self, new_language):
        global language
        self.current_language = new_language
        language = new_language

        # Update placeholder text and send button text based on selected language
        self.entry.setPlaceholderText(self.placeholder_texts.get(new_language, "Type your message here..."))
        self.send_button.setText(self.send_button_texts.get(new_language, "Send"))
        self.voice_label.setText(self.voice_switch_texts.get(new_language, "Voice: "))

    def handle_request(self):
        user_input = self.entry.text().strip()
        if not user_input:
            self.chat_display.append("[Error] Please enter a message.")
            return

        self.send_button.setEnabled(False)
        self.entry.clear()

        try:
            agent_type = agent_selector(self.chat_bot, user_input)
            self.worker = ChatWorker(self.chat_bot, agent_type, user_input)
            self.worker.finished.connect(self.handle_response)
            self.worker.error.connect(self.handle_error)
            self.worker.start()

        except Exception as e:
            self.handle_error(str(e))

    def handle_response(self, result):
        agent_type, response = result
        if agent_type == "linux_command":
            cmd, description, terminal_output = response
            self.chat_display.append(f"Arch Chan: Command: {cmd}\nDescription: {description}\nTerminal Output: {terminal_output}\n")
        elif agent_type == "weather_gether":
            self.chat_display.append(f"Arch Chan: {response}\n")
        elif agent_type == "friend_chat":
            self.chat_display.append(f"Arch Chan: {response}\n")

        # Only play voice if voice_active is True
        if self.voice_active:
            voice_lang = {
                "English": "en",
                "Turkish": "tr",
                "Spanish": "es",
                "German": "de",
                "French": "fr",
                "Russian": "ru"
            }

            print(voice_lang[language])
            play_voice(
                text=response,
                volume=0.5,
                lang=voice_lang[language]
            )

        self.send_button.setEnabled(True)

    def handle_error(self, error_message):
        self.chat_display.append(f"[Error] {error_message}")
        self.send_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('/usr/share/Arch-Chan-AI/icons/arch-chan_mini.png'))

    try:
        window = ChatBotGUI()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical(f"Application crashed: {e}")
        QMessageBox.critical(None, "Fatal Error", f"Application crashed: {e}")
        sys.exit(1)
