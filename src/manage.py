"""Local administrative CLI for Work Control Plane.

Run from the project root, for example:
    python -m src.manage user list

This is an administrator-only tool: do not expose it as a web endpoint.
"""

import argparse
from typing import TypeVar, NoReturn
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db import (
    Family,
    FamilyMembership,
    Role,
    RolePermission,
    User,
    engine,
    Base
)

T = TypeVar("T", bound=Base)

def fail(message: str) -> NoReturn:
    raise SystemExit(f"Ошибка: {message}")


def get_existing(session: Session, model: type[T], key: int | str) -> T:
    instance: T | None = session.get(model, key)
    if instance is None:
        fail(f"{model.__name__} ({key}) не найден")
    return instance


def print_rows(headers: tuple[str, ...], rows) -> None:
    print("\t".join(headers))
    for row in rows:
        print("\t".join(str(value) for value in row))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Work Control Plane: администрирование")
    # manage.py (section)
    first_level_parser = parser.add_subparsers(dest="section", required=True)
    # manage.py (section)role
    roles_parser = first_level_parser.add_parser("role", help="Роли и разрешения")
    # manage.py (section)role (action)
    roles_action_parser = roles_parser.add_subparsers(dest="action", required=True)
    # manage.py (section)role (action)list
    roles_action_parser.add_parser("list")
    # manage.py (section)role (action)create
    cmd = roles_action_parser.add_parser("create")
    # manage.py (section)role (action)create "name"
    cmd.add_argument("name")
    # manage.py (section)role (action)grant
    # manage.py (section)role (action)revoke
    for action in ("grant", "revoke"):
        cmd = roles_action_parser.add_parser(action)
        # manage.py (section)role (action)grant|revoke "name"
        cmd.add_argument("name")
        # manage.py (section)role (action)grant|revoke "name" "permission"
        cmd.add_argument("permission")
    # manage.py (section)role (action)show
    cmd = roles_action_parser.add_parser("show")
    # manage.py (section)role (action)show "name"
    cmd.add_argument("name")

    # manage.py (section)user
    users_parser = first_level_parser.add_parser("user", help="Пользователи")
    # manage.py (section)user (action)
    users_action_parser = users_parser.add_subparsers(dest="action", required=True)
    # manage.py (section)user (action)create
    cmd = users_action_parser.add_parser("create")
    # manage.py (section)user (action)create "name"
    cmd.add_argument("name")
    # manage.py (section)user (action)create "name" --family FAMILY_ID
    cmd.add_argument("--family", type=int, metavar="FAMILY_ID")
    # manage.py (section)user (action)create "name" --family FAMILY_ID --role ROLE
    cmd.add_argument("--role", metavar="ROLE", help="Только вместе с --family (по умолчанию user)")
    # manage.py (section)user (action)list
    cmd = users_action_parser.add_parser("list")
    # manage.py (section)user (action)list --family FAMILY_ID
    cmd.add_argument("--family", type=int, metavar="FAMILY_ID")
    # manage.py (section)user (action)find
    cmd = users_action_parser.add_parser("find")
    search = cmd.add_mutually_exclusive_group(required=True)
    # ИЛИ
    # manage.py (section)user (action)find "user_id"
    search.add_argument("user_id", type=int, nargs="?")
    # ИЛИ
    # manage.py (section)user (action)find --family FAMILY_ID
    search.add_argument("--family", type=int, metavar="FAMILY_ID")

    # manage.py (section)family
    families_parser = first_level_parser.add_parser("family", help="Семьи и членство")
    # manage.py (section)family (action)
    families_action_parser = families_parser.add_subparsers(dest="action", required=True)
    # manage.py (section)family (action)list
    families_action_parser.add_parser("list")
    # manage.py (section)family (action)create
    cmd = families_action_parser.add_parser("create")
    # manage.py (section)family (action)create "name"
    cmd.add_argument("name")
    # manage.py (section)family (action)create "name" --admin USER_ID
    cmd.add_argument("--admin", type=int, required=True, metavar="USER_ID")
    # manage.py (section)family (action)find
    cmd = families_action_parser.add_parser("find")
    # manage.py (section)family (action)find --user USER_ID
    cmd.add_argument("--user", required=True, type=int, metavar="USER_ID")
    # manage.py (section)family (action)members
    cmd = families_action_parser.add_parser("members")
    # manage.py (section)family (action)members "family_id"
    cmd.add_argument("family_id", type=int)
    # manage.py (section)family (action)add-member
    cmd = families_action_parser.add_parser("add-member")
    # manage.py (section)family (action)add-member --family INT
    cmd.add_argument("--family", required=True, type=int, metavar="FAMILY_ID")
    # manage.py (section)family (action)add-member --family INT --user INT
    cmd.add_argument("--user", required=True, type=int, metavar="USER_ID")
    # manage.py (section)family (action)add-member --family INT --user INT --role ROLE
    cmd.add_argument("--role", metavar="ROLE", default="user", help=" (по умолчанию user)")
    # manage.py (section)family (action)set-role --family_id FAMILY_ID --user_id USER_ID --role ROLE
    cmd = families_action_parser.add_parser("set-role")
    cmd.add_argument("--family", required=True, type=int, metavar="FAMILY_ID")
    cmd.add_argument("--user", required=True, type=int, metavar="USER_ID")
    cmd.add_argument("--role", required=True, metavar="ROLE")
    # manage.py (section)family (action)remove-member --family FAMILY_ID --user USER_ID
    cmd = families_action_parser.add_parser("remove-member")
    cmd.add_argument("--family", required=True, type=int, metavar="FAMILY_ID")
    cmd.add_argument("--user", required=True, type=int, metavar="USER_ID")
    return parser


def manage_role(session: Session, args: argparse.Namespace) -> None:
    if args.action == "list":
        print_rows(("ROLE",), [(x,) for x in session.scalars(select(Role.name).order_by(Role.name))])
    elif args.action == "create":
        name = args.name.strip()
        if not name:
            fail("Название роли не может быть пустым")
        if session.get(Role, name):
            fail(f"Роль {name!r} уже существует")
        session.add(Role(name=name))
        print(f"Роль создана: {name}")
    elif args.action == "show":
        get_existing(session, Role, args.name)
        stmt = select(RolePermission.permission).where(
            RolePermission.role == args.name
        ).order_by(RolePermission.permission)
        print_rows(("PERMISSION",), [(x,) for x in session.scalars(stmt)])
    else:
        get_existing(session, Role, args.name)
        key = (args.name, args.permission)
        existing = session.get(RolePermission, key)
        if args.action == "grant":
            if existing:
                print("Разрешение уже назначено")
            else:
                session.add(RolePermission(role=args.name, permission=args.permission))
                print(f"Разрешение добавлено: {args.name} → {args.permission}")
        elif args.action == "revoke":
            if existing is None:
                print("Такого разрешения у роли нет")
            else:
                session.delete(existing)
                print(f"Разрешение убрано: {args.name} → {args.permission}")


def manage_user(session: Session, args: argparse.Namespace) -> None:
    if args.action == "list":
        if args.family is None:
            stmt = select(User.id, User.name).order_by(User.id)
            print_rows(("USER_ID", "NAME"), session.execute(stmt))
        else:
            get_existing(session, Family, args.family)
            stmt = (
                select(User.id, User.name, FamilyMembership.role)
                .join(FamilyMembership, FamilyMembership.user_id == User.id)
                .where(FamilyMembership.family_id == args.family)
                .order_by(User.id)
            )
            print_rows(("USER_ID", "NAME", "ROLE"), session.execute(stmt))
    elif args.action == "find":
        get_existing(session, User, args.user_id)
        stmt = (
            select(Family.id, Family.name, FamilyMembership.role)
            .join(FamilyMembership, FamilyMembership.family_id == Family.id)
            .where(FamilyMembership.user_id == args.user_id)
            .order_by(Family.id)
        )
        print_rows(("FAMILY_ID", "NAME", "ROLE"), session.execute(stmt))
    elif args.action == "create":
        name = args.name.strip()
        if not name:
            fail("Имя пользователя не может быть пустым")
        if args.role and args.family is None:
            fail("Указывать --role можно только вместе с --family")
        if args.family is not None:
            get_existing(session, Family, args.family)
            role_name = args.role or "user"
            get_existing(session, Role, role_name)
        user = User(name=name)
        session.add(user)
        session.flush()
        if args.family is not None:
            session.add(FamilyMembership(
                family_id=args.family, user_id=user.id, role=role_name
            ))
        print(f"Пользователь создан: id={user.id}, имя={name}")


def manage_family(session: Session, args: argparse.Namespace) -> None:
    if args.action == "list":
        stmt = select(Family.id, Family.name).order_by(Family.id)
        print_rows(("FAMILY_ID", "NAME"), session.execute(stmt))
    elif args.action == "create":
        name = args.name.strip()
        if not name:
            fail("Название семьи не может быть пустым")
        get_existing(session, User, args.admin)
        get_existing(session, Role, "admin")
        family = Family(name=name)
        session.add(family)
        session.flush()
        session.add(FamilyMembership(
            family_id=family.id, user_id=args.admin, role="admin"
        ))
        print(f"Семья создана: id={family.id}, название={name}; администратор={args.admin}")
    else:
        get_existing(session, Family, args.family_id)
        if args.action == "members":
            stmt = (
                select(User.id, User.name, FamilyMembership.role)
                .join(FamilyMembership, FamilyMembership.user_id == User.id)
                .where(FamilyMembership.family_id == args.family_id)
                .order_by(User.id)
            )
            print_rows(("USER_ID", "NAME", "ROLE"), session.execute(stmt))
            return
        get_existing(session, User, args.user_id)
        membership = session.get(FamilyMembership, (args.user_id, args.family_id))
        if args.action == "add-member":
            get_existing(session, Role, args.role)
            if membership:
                fail("Пользователь уже состоит в этой семье; используйте set-role")
            session.add(FamilyMembership(
                user_id=args.user_id, family_id=args.family_id, role=args.role
            ))
            print("Участник добавлен")
        elif args.action in ("set-role", "remove-member"):
            if membership is None:
                fail("Пользователь не состоит в этой семье")
            if args.action == "set-role":
                get_existing(session, Role, args.role)
            removing_admin = membership.role == "admin" and (
                args.action == "remove-member" or args.role != "admin"
            )
            if removing_admin:
                other_admin = session.scalar(
                    select(FamilyMembership.user_id).where(
                        FamilyMembership.family_id == args.family_id,
                        FamilyMembership.role == "admin",
                        FamilyMembership.user_id != args.user_id,
                    ).limit(1)
                )
                if other_admin is None:
                    fail("Нельзя убрать последнего администратора семьи")
            if args.action == "set-role":
                membership.role = args.role
                print("Роль участника изменена")
            else:
                session.delete(membership)
                print("Участник исключён из семьи (сам пользователь не удалён)")


def main() -> None:
    args = build_parser().parse_args()
    # The whole operation is one transaction, including family creation and admin assignment.
    with Session(engine) as session, session.begin():
        if args.section == "role":
            manage_role(session, args)
        elif args.section == "user":
            manage_user(session, args)
        elif args.section == "family":
            manage_family(session, args)


if __name__ == "__main__":
    main()