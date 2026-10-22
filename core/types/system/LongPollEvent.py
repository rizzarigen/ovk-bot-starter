class LongPollEvent:
    
    def __init__(self, data: list):
        self.type_code = data[0]
        self.update = data[1:]
    
    @property
    def message_id(self):
        return self.update[0]
    
    @property    
    def peer_id(self):
        return self.update[2]
    
    @property
    def timestamp(self):
        return self.update[3]
    
    @property
    def text(self):
        return self.update[5]
    
    @property
    def extra_fields(self):
        return self.update[6] if len(self.update) > 6 and isinstance(self.update[6], dict) else {}
    