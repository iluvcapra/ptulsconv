from .doc_entity import SessionDescriptor

class ADRDocument:
    def __init__(self, session: SessionDescriptor):
        self.document = session
