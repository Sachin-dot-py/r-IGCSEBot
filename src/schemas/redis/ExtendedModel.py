from redis_om import JsonModel

class ExtendedModel(JsonModel):
    def __getitem__(self, key):
        return getattr(self, key)
    
    def __setitem__(self, key, value):
        setattr(self, key, value)