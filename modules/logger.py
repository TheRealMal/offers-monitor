from datetime import datetime

class Logger():
    def __init__(self) -> None:
        self.pattern = "[{}] {}"
    
    def log(self, msg: str) -> None:
        print(self.pattern.format(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), msg))