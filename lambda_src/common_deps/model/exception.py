class ScrappingError(Exception):
    def __init__(self, body_html=None):
        self.body_html = body_html

