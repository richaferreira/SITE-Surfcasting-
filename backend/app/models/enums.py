from enum import StrEnum


class RoleCode(StrEnum):
    ADMIN = "ADMIN"
    AUTHOR = "AUTHOR"
    USER = "USER"


class BeachProfile(StrEnum):
    TOMBO = "TOMBO"
    INTERMEDIARIA = "INTERMEDIARIA"
    RASA = "RASA"
    ABRIGADA = "ABRIGADA"
