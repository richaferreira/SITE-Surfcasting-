from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.security import hash_password  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.models.enums import RoleCode  # noqa: E402
from app.models.user import User  # noqa: E402
from app.repositories.user import UserRepository  # noqa: E402
from app.schemas.auth import UserRegistration  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cria o primeiro administrador do backoffice.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--email", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    password = getpass.getpass("Senha: ")
    confirmation = getpass.getpass("Confirme a senha: ")
    if password != confirmation:
        raise SystemExit("As senhas não coincidem.")

    payload = UserRegistration(
        name=args.name,
        username=args.username,
        email=args.email,
        password=password,
    )

    with SessionLocal() as session:
        repository = UserRepository(session)
        if repository.get_by_email(str(payload.email).lower()) is not None:
            raise SystemExit("Já existe um usuário com este e-mail.")
        if repository.get_by_username(payload.username) is not None:
            raise SystemExit("Já existe um usuário com este nome de usuário.")

        role = repository.get_role(RoleCode.ADMIN.value)
        if role is None:
            raise SystemExit("Role ADMIN ausente. Execute o schema inicial do banco.")

        admin = User(
            role_id=role.id,
            name=payload.name,
            username=payload.username,
            email=str(payload.email).lower(),
            password_hash=hash_password(payload.password),
            is_active=True,
        )
        repository.add(admin)
        session.commit()
        print(f"Administrador criado: {admin.username}")


if __name__ == "__main__":
    main()
