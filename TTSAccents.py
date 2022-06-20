

class TTSAccents:
    def __init__(self) -> None:
        self.accents = {
            "US": "com",
            "AU": "com.au",
            "UK": "co.uk",
            "CA": "ca",
            "IN": "co.in",
            "IE": "ie",
            "SA": "co.za"
        }

        self.current_accent = self.accents["US"]
        