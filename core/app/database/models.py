import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, String, Float, Boolean, Enum as SqlEnum, Integer, Date
from enum import Enum
import uuid


class BaseModelOrm(DeclarativeBase):
    pass


class AuthPrivilegesOrm(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class UserTypesOrm(str, Enum):
    COMMERCIAL = "COMMERCIAL"
    PRIVATE = "PRIVATE"


class WorkTypesOrm(str, Enum):
    FLYERS = "FLYERS"
    CALLS = "CALLS"
    SHOW = "SHOW"
    MEET = "MEET"
    DEAL_RENT = "DEAL_RENT"
    DEAL_SALE = "DEAL_SALE"
    DEPOSIT = "DEPOSIT"
    SEARCH = "SEARCH"
    ANALYTICS = "ANALYTICS"
    OTHER = "OTHER"
    REGULAR_CONTRACT = "REGULAR_CONTRACT"
    EXCLUSIVE_CONTRACT = "EXCLUSIVE_CONTRACT"


class KpiLevelsOrm(str, Enum):
    TRAINEE = "TRAINEE"
    SPECIALIST = "SPECIALIST"
    EXPERT = "EXPERT"
    TOP = "TOP"


class UserStatusesOrm(str, Enum):
    OWNER = "OWNER"
    USER = "USER"


class FileAccessModeOrm(str, Enum):
    READ = "READ"
    WRITE = "WRITE"


class UserCredentialsOrm(BaseModelOrm):
    __tablename__ = 'user_credentials'
    __table_args__ = {'schema': 'auth'}

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4()))
    login: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    privileges: Mapped[AuthPrivilegesOrm] = mapped_column(
        SqlEnum(AuthPrivilegesOrm), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class TokenOrm(BaseModelOrm):
    __tablename__ = 'tokens'
    __table_args__ = {'schema': 'auth'}

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        String, ForeignKey('auth.user_credentials.id'))
    token: Mapped[str] = mapped_column(String, nullable=False)
    is_regular: Mapped[bool] = mapped_column(Boolean, default=False)


class VersionOrm(BaseModelOrm):
    __tablename__ = "versions"
    __table_args__ = {'schema': 'public'}

    suported_version: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4()))


class FileOrm(BaseModelOrm):
    __tablename__ = 'files'
    __table_args__ = {'schema': 'public'}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    obj_name: Mapped[str] = mapped_column(String)
    bucket_name: Mapped[str] = mapped_column(String)

    # calls: Mapped[list["CallOrm"]] = relationship(
    #     "СallOrm", back_populates="file")


class UserOrm(BaseModelOrm):
    __tablename__ = "users"
    __table_args__ = {'schema': 'public'}

    id: Mapped[str] = mapped_column(String(36), ForeignKey(
        'auth.user_credentials.id'), primary_key=True, index=True)
    type: Mapped[UserTypesOrm] = mapped_column(SqlEnum(UserTypesOrm))
    email: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String, default="Пользователь")
    gender: Mapped[str | None] = mapped_column(String, nullable=True)
    birthday: Mapped[int | None] = mapped_column(Integer, nullable=True)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    image: Mapped[str | None] = mapped_column(ForeignKey(FileOrm.id))

    # notes: Mapped[list["NoteOrm"]] = relationship(
    #     "NoteOrm", back_populates="user", cascade="all, delete-orphan")
    # tasks: Mapped[list["TaskOrm"]] = relationship(
    #     "TaskOrm", back_populates="user", cascade="all, delete-orphan")
    # teams: Mapped[list["UserTeamOrm"]] = relationship(
    #     "UserTeamOrm", back_populates="user", cascade="all, delete-orphan")
    # statistics: Mapped[list["StatisticOrm"]] = relationship(
    #     "StatisticOrm", back_populates="user", cascade="all, delete-orphan")
    # addresses: Mapped[list["AddressOrm"]] = relationship(
    #     "AddressOrm", back_populates="user", cascade="all, delete-orphan")
    # calls: Mapped[list["CallOrm"]] = relationship(
    #     "СallOrm", back_populates="user", cascade="all, delete-orphan")
    # kpi: Mapped[list["KpiOrm"]] = relationship(
    #     "KpiOrm", back_populates="user", cascade="all, delete-orphan")


class NoteOrm(BaseModelOrm):
    __tablename__ = "notes"
    __table_args__ = {'schema': 'public'}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        ForeignKey(UserOrm.id, ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[int] = mapped_column(Integer)

    # user: Mapped["UserOrm"] = relationship("UserOrm", back_populates="notes")


class TaskOrm(BaseModelOrm):
    __tablename__ = "tasks"
    __table_args__ = {'schema': 'public'}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        ForeignKey(UserOrm.id, ondelete="CASCADE"))
    work_type: Mapped[WorkTypesOrm] = mapped_column(SqlEnum(WorkTypesOrm))
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[int] = mapped_column(Integer)
    duration_seconds: Mapped[int] = mapped_column(Integer)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    # user: Mapped["UserOrm"] = relationship("UserOrm", back_populates="tasks")


class TeamOrm(BaseModelOrm):
    __tablename__ = "teams"
    __table_args__ = {'schema': 'public'}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String)
    created_at: Mapped[int] = mapped_column(Integer)

    # users: Mapped[list["UserTeamOrm"]] = relationship(
    #     "UserTeamOrm", back_populates="team", cascade="all, delete-orphan")


class UserTeamOrm(BaseModelOrm):
    __tablename__ = "user_teams"
    __table_args__ = {'schema': 'public'}

    team_id: Mapped[str] = mapped_column(ForeignKey(
        TeamOrm.id, ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey(
        UserOrm.id, ondelete="CASCADE"), primary_key=True)
    role: Mapped[UserStatusesOrm] = mapped_column(SqlEnum(UserStatusesOrm))

    # team: Mapped["TeamOrm"] = relationship("TeamOrm", back_populates="users")
    # user: Mapped["UserOrm"] = relationship("UserOrm", back_populates="teams")


class FilesAccessOrm(BaseModelOrm):
    __tablename__ = 'files_access'
    __table_args__ = {'schema': 'public'}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey(UserOrm.id))
    file_id: Mapped[str] = mapped_column(
        ForeignKey(FileOrm.id, ondelete="CASCADE"))
    file_access_mode: Mapped[FileAccessModeOrm] = mapped_column(
        SqlEnum(FileAccessModeOrm), default=FileAccessModeOrm.READ)


class StatisticOrm(BaseModelOrm):
    __tablename__ = "statistics"
    __table_args__ = {'schema': 'public'}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        ForeignKey(UserOrm.id, ondelete="CASCADE"))
    date_time: Mapped[int] = mapped_column(
        Integer, default=int(datetime.datetime.now().timestamp()))
    work_type: Mapped[WorkTypesOrm] = mapped_column(SqlEnum(WorkTypesOrm))
    comment: Mapped[str | None] = mapped_column(String, default=None)
    count: Mapped[int] = mapped_column(Integer, default=0)
    is_archive: Mapped[bool] = mapped_column(Boolean, default=False)

    # user: Mapped["UserOrm"] = relationship(
    #     "UserOrm", back_populates="statistics")


class AddressOrm(BaseModelOrm):
    __tablename__ = "addresses"
    __table_args__ = {'schema': 'public'}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        ForeignKey(UserOrm.id, ondelete="CASCADE"))
    address: Mapped[str] = mapped_column(String, default="")
    lat: Mapped[float] = mapped_column(Float, default=0.0)
    lon: Mapped[float] = mapped_column(Float, default=0.0)
    date_time: Mapped[int] = mapped_column(Integer, default=0)

    # user: Mapped["UserOrm"] = relationship(
    #     "UserOrm", back_populates="addresses")


class KpiOrm(BaseModelOrm):
    __tablename__ = "kpi"
    __table_args__ = {'schema': 'public'}

    user_id: Mapped[str] = mapped_column(ForeignKey(
        UserOrm.id, ondelete="CASCADE"), primary_key=True)
    kpi_level: Mapped[KpiLevelsOrm] = mapped_column(SqlEnum(KpiLevelsOrm))
    base_salary_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    kpi: Mapped[float] = mapped_column(Float, default=0.0)

    # user: Mapped["UserOrm"] = relationship("UserOrm", back_populates="kpi")


class CallOrm(BaseModelOrm):
    __tablename__ = 'calls'
    __table_args__ = {'schema': 'public'}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        ForeignKey(UserOrm.id, ondelete="CASCADE"))
    date_time: Mapped[int] = mapped_column(Integer)
    phone_number: Mapped[str] = mapped_column(String)
    contact_name: Mapped[str] = mapped_column(String)
    length_seconds: Mapped[int] = mapped_column(Integer)
    call_type: Mapped[int] = mapped_column(Integer)
    transcription: Mapped[str | None] = mapped_column(
        String, default=None)
    file_id: Mapped[str | None] = mapped_column(ForeignKey(FileOrm.id))

    # user: Mapped["UserOrm"] = relationship("UserOrm", back_populates="calls")
    # file: Mapped["FileOrm"] = relationship("FileOrm", back_populates="calls")
