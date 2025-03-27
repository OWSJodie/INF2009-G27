from gtts import gTTS

# The text you want to convert to speech
text = "The bar is tilting to the right. Please adjust your form."

# Create a gTTS object
tts = gTTS(text=text, lang='en')

# Save the audio to a file
tts.save("bar_right.mp3")

print("✅ Audio saved as bar_left.mp3")
