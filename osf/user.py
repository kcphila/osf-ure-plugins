from . import OSFBase

class User(OSFBase):

    json_properties = ['id', 'links', 'type', 'attributes', 'relationships']
    def __init__(self, init, session):
        self._projects = None

        self.session = session
        if type(init) is dict:
            self.process_json(init)
            self._user_id = self.id
        else:
            self._user_id = init

    @property
    def user_id(self):
        return(self._user_id)

    @property
    def projects(self):
        return([p for p in self.nodes if p.project_type == 'project'])

    @property
    def nodes(self):
        if not self._projects:
            data = self.session.get_all(self.session.root + '/users/'+self.user_id+'/nodes/')
            self._projects = [osf.Project(p, self.session) for p in data]
        return(self._projects)

    def get_project(self, project_id):
        for p in self.projects:
            if p.id == project_id:
                return(p)
