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


class FishingPointType(StrEnum):
    BURACO = "BURACO"
    COROA_AREIA = "COROA_AREIA"
    CANAL_RETORNO = "CANAL_RETORNO"
    ESTRUTURA = "ESTRUTURA"
    OUTRO = "OUTRO"


class AccessibilityLevel(StrEnum):
    FACIL = "FACIL"
    MODERADA = "MODERADA"
    DIFICIL = "DIFICIL"
    RESTRITA = "RESTRITA"


class PostContentType(StrEnum):
    ARTIGO = "ARTIGO"
    TUTORIAL = "TUTORIAL"
    VIDEO = "VIDEO"
    EQUIPAMENTO = "EQUIPAMENTO"


class PostStatus(StrEnum):
    RASCUNHO = "RASCUNHO"
    EM_REVISAO = "EM_REVISAO"
    PUBLICADO = "PUBLICADO"
    ARQUIVADO = "ARQUIVADO"


class MediaKind(StrEnum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
