import io
from pydub import AudioSegment
import speech_recognition as sr

async def process_audio_data(audio_data: bytes) -> str:
    recognizer = sr.Recognizer()
    audio_file = io.BytesIO(audio_data)

    # Конвертация байтов в аудиоформат, который поддерживает pydub и speech_recognition
    audio_segment = AudioSegment.from_file(audio_file, format="ogg")
    audio_wav = io.BytesIO()
    audio_segment.export(audio_wav, format="wav")
    audio_wav.seek(0)

    with sr.AudioFile(audio_wav) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio, language="ru-RU")
            return text
        except sr.UnknownValueError:
            return "Не удалось распознать речь"
        except sr.RequestError as e:
            return f"Ошибка сервиса распознавания речи: {e}"