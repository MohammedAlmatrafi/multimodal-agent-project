from openai import OpenAI

client = OpenAI()


def transcribe_audio(file_path: str) -> str:
    with open(file_path, "rb") as f:
        transcription = client.audio.transcriptions.create(model="whisper-1", file=f)
    return transcription.text


# model = whisper.load_model(
#     "small"
# )  # You can use "small" or "medium" for better accuracy


# def transcribe_audio(file_path: str):
#     print("Attempting transcribe of: ", file_path)
#     print("Exists:", os.path.exists(file_path))
#     result = model.transcribe(file_path)
#     with open(file_path + ".txt", "w", encoding="utf-8") as f:
#         f.write(result["text"])
#     return result["text"]
