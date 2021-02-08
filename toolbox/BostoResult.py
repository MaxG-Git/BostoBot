class BostoResult:

    def __init__(self, result:bool, reason:str = None, error=None, **kwargs):
        self.result = result
        self.reason = reason
        self.error = error
    
