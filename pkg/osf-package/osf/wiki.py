from . import OSFBase

class Wiki(OSFBase):
    """A python class to represent an OSF Project Wiki
    """

    json_properties = ['attributes', 'id', 'links', 'relationships', 'type']

    def __init__(self, jref, session):
        self.session = session
        self.process_json(jref)

    @property
    def date_modified(self):
        return(self.json['attributes']['date_modified'])

    @property
    def kind(self) -> str:
        return(self.json['attributes']['kind'])        

    @property
    def name(self) -> str:
        if 'name' in self.json['attributes']: 
            return(self.json['attributes']['name'])


    @property
    def extra(self) -> str:
        return(self.json['attributes']['extra'])


    @property
    def content_type(self) -> str:
        return(self.json['attributes']['content_type'])


    @property
    def path(self) -> str:
        return(self.json['attributes']['path'])

    @property
    def current_user_can_comment(self) -> bool:
        return(self.json['attributes']['current_user_can_comment'])

    @property
    def materialized_path(self) -> str:
        return(self.json['attributes']['materialized_path'])

    @property
    def size(self) -> int:
        return(self.json['attributes']['size'])

