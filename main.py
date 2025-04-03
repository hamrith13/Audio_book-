import pyttsx3
import PyPDF2
from tkinter.filedialog import askopenfilename

# Open file dialog to select PDF
book = askopenfilename()
pdfreader = PyPDF2.PdfReader(book)  # Updated class name in new PyPDF2
pages = len(pdfreader.pages)  # Updated attribute

# Initialize the text-to-speech engine once
player = pyttsx3.init()

for num in range(pages):
    page = pdfreader.pages[num]
    text = page.extract_text()  # Updated method
    if text.strip():  # Ensure only non-empty text is spoken
        player.say(text)

player.runAndWait()  # Run the speech engine after processing all pages
