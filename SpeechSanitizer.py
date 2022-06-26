

from mimetypes import init
import re


class SpeechSanitizer:
    
    def sanitize(self, text):
        new_text = text
        for item in self.regex.finditer(text):
            matchText = item.group(0)
            pos = item.span()
            
            if matchText.startswith("<:"):
                emoji_name = item.group(1)
                new_text = f"{new_text[:pos[0]]} {emoji_name} {new_text[pos[1]:]}"
                
            
    
    def __init__(self):
        self.regex = re.compile("(<(?::(\w+):\d+|@\d+|#\d+)>|http\S+)")
