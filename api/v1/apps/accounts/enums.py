from enum import Enum


class UserRole(Enum):
    p = 'Project Owner'
    d = 'Director'
    m = 'Manager'
    w = 'Worker'

    @classmethod
    def choices(cls):
        return ((i.name, i.value) for i in cls)
