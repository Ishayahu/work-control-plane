import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from datetime import date
from decimal import Decimal
from uuid import UUID
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    ForeignKey,
    Identity,
    Integer,
    LargeBinary,
    Numeric,
    Text,
    select,
    text, false,
    Boolean,
    Uuid
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


load_dotenv(Path(__file__).parent.parent / ".env")

db_url = URL.create(
    drivername="postgresql+psycopg",
    username="wcp_app",
    password=os.environ.get("WCP_DB_PASSWORD"),
    host="localhost",
    port=5432,
    database="work_control_plane",
)
engine = create_engine(db_url)



class Base(DeclarativeBase):
    pass


class Family(Base):
    __tablename__ = "families"

    id: Mapped[int] = mapped_column(
        BigInteger, Identity(), primary_key=True
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger, Identity(), primary_key=True
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)

    def has_permission(
        self,
        session: Session,
        permission: str,
        family_id: int | None = None,
    ) -> bool:
        if family_id is None:
            # Personal context: standard "user" permissions.
            stmt = select(RolePermission.permission).where(
                RolePermission.role == "user",
                RolePermission.permission == permission,
            )
        else:
            # Family context: permissions of the user's role
            # in the specified family.
            stmt = (
                select(RolePermission.permission)
                .join(
                    FamilyMembership,
                    FamilyMembership.role == RolePermission.role,
                )
                .where(
                    FamilyMembership.user_id == self.id,
                    FamilyMembership.family_id == family_id,
                    RolePermission.permission == permission,
                )
            )

        return session.scalar(stmt.limit(1)) is not None


class FamilyMembership(Base):
    __tablename__ = "family_memberships"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True
    )
    family_id: Mapped[int] = mapped_column(
        ForeignKey("families.id"), primary_key=True
    )
    role: Mapped[str] = mapped_column(Text, ForeignKey("roles.name"), nullable=False)


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role: Mapped[str] = mapped_column(Text, ForeignKey("roles.name"), nullable=False)
    permission: Mapped[str] = mapped_column(Text, primary_key=True)


class Role(Base):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(Text, primary_key=True)


class ModelRun(Base):
    __tablename__ = "model_runs"

    id: Mapped[int] = mapped_column(
        BigInteger, Identity(), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    family_id: Mapped[int | None] = mapped_column(
        ForeignKey("families.id"), nullable=True
    )

    execution_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    prefetch_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=false()
    )

    date: Mapped[date] = mapped_column(Date, nullable=False)
    request_encrypted: Mapped[bytes] = mapped_column(
        LargeBinary, nullable=False
    )
    call_kind: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(Text, nullable=False)
    effort: Mapped[str] = mapped_column(Text, nullable=False)

    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    cost_rub: Mapped[Decimal] = mapped_column(
        Numeric(18, 8), nullable=False
    )
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)

if __name__ == "__main__":
    # Base.metadata.create_all(engine)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT current_user, current_database()"))
        for row in result:
            print(row)