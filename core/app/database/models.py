import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, Column, Integer, String, Float, Boolean, Enum as SqlEnum
from enum import Enum
import uuid


class BaseModelOrm(DeclarativeBase):
    pass


class AuthPrivilegesOrm(Enum):
    USER = "Пользователь"
    ADMIN = "Администратор"


class UserTypesOrm(Enum):
    COMMERCIAL = "Риелтор коммерческой недвижимости"
    PRIVATE = "Риелтор частной недвижимости"


class WorkTypesOrm(Enum):
    FLYERS = "Рассклейка"
    CALLS = "Обзвон"
    SHOW = "Показ объекта"
    MEET = "Встреча по объекту"
    DEAL_RENT = "Сделка по аренде"
    DEAL_SALE = "Сделка по продаже"
    DEPOSIT = "Получение задатка"
    SEARCH = "Поиск объектов"
    ANALYTICS = "Аналитика рынка"
    OTHER = "Нечто особенное"
    REGULAR_CONTRACT = "Обычный договор"
    EXCLUSIVE_CONTRACT = "Эксклюзивный договор"


class KpiLevelsOrm(Enum):
    DAY = "День"
    WEEK = "Неделя"
    MONTH = "Месяц"


class StatisticPeriodOrm(Enum):
    TRAINEE = "Стажер"
    SPECIALIST = "Специалист"
    EXPERT = "Эксперт"
    TOP = "ТОП"


class UserStatusesOrm(Enum):
    OWNER = "Владелец"
    USER = "Участник"


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
        DateTime, default=datetime.datetime.utcnow)
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


class FileOrm(BaseModelOrm):
    __tablename__ = 'files'
    __table_args__ = {'schema': 'public'}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    obj_key: Mapped[str] = mapped_column(String)
    obj_name: Mapped[str] = mapped_column(String)
    bucket_name: Mapped[str] = mapped_column(String)


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
    image: Mapped[str] = mapped_column(ForeignKey(FileOrm.id), default="1")

    credentials: Mapped[list["UserCredentialsOrm"]] = relationship(
        "UserCredentialsOrm", back_populates="user")
    tokens: Mapped[list["TokenOrm"]] = relationship(
        "TokenOrm", back_populates="user")
    notes: Mapped[list["NoteOrm"]] = relationship(
        "NoteOrm", back_populates="user")
    tasks: Mapped[list["TaskOrm"]] = relationship(
        "TaskOrm", back_populates="user")
    teams: Mapped[list["UserTeamOrm"]] = relationship(
        "UserTeamOrm", back_populates="user")
    statistics: Mapped[list["StatisticOrm"]] = relationship(
        "StatisticOrm", back_populates="user")
    addresses: Mapped[list["AddressOrm"]] = relationship(
        "AddressOrm", back_populates="user")
    calls: Mapped[list["СallOrm"]] = relationship(
        "CallOrm", back_populates="user")


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

    user: Mapped["UserOrm"] = relationship("UserOrm", back_populates="notes")


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

    user: Mapped["UserOrm"] = relationship("UserOrm", back_populates="tasks")


class TeamOrm(BaseModelOrm):
    __tablename__ = "teams"
    __table_args__ = {'schema': 'public'}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String)
    created_at: Mapped[int] = mapped_column(Integer)

    users: Mapped[list["UserTeamOrm"]] = relationship(
        "UserTeamOrm", back_populates="team")


class UserTeamOrm(BaseModelOrm):
    __tablename__ = "user_teams"
    __table_args__ = {'schema': 'public'}

    team_id: Mapped[str] = mapped_column(ForeignKey(
        TeamOrm.id, ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey(
        UserOrm.id, ondelete="CASCADE"), primary_key=True)
    role: Mapped[UserStatusesOrm] = mapped_column(SqlEnum(UserStatusesOrm))

    team: Mapped["TeamOrm"] = relationship("TeamOrm", back_populates="users")
    user: Mapped["UserOrm"] = relationship("UserOrm", back_populates="teams")


class StatisticOrm(BaseModelOrm):
    __tablename__ = "statistics"
    __table_args__ = {'schema': 'public'}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        ForeignKey(UserOrm.id, ondelete="CASCADE"))
    period_type: Mapped[StatisticPeriodOrm] = mapped_column(
        SqlEnum(StatisticPeriodOrm))
    flyers: Mapped[int] = mapped_column(Integer, default=0)
    calls: Mapped[int] = mapped_column(Integer, default=0)
    shows: Mapped[int] = mapped_column(Integer, default=0)
    meets: Mapped[int] = mapped_column(Integer, default=0)
    deals_rent: Mapped[int] = mapped_column(Integer, default=0)
    deals_sale: Mapped[int] = mapped_column(Integer, default=0)
    deposits: Mapped[int] = mapped_column(Integer, default=0)
    searches: Mapped[int] = mapped_column(Integer, default=0)
    analytics: Mapped[int] = mapped_column(Integer, default=0)
    others: Mapped[int] = mapped_column(Integer, default=0)
    regular_contracts: Mapped[int] = mapped_column(Integer, default=0)
    exclusive_contracts: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped["UserOrm"] = relationship(
        "UserOrm", back_populates="statistics")


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

    user: Mapped["UserOrm"] = relationship(
        "UserOrm", back_populates="addresses")


class KpiOrm(BaseModelOrm):
    __tablename__ = "kpi"
    __table_args__ = {'schema': 'public'}

    user_id: Mapped[str] = mapped_column(ForeignKey(
        UserOrm.id, ondelete="CASCADE"), primary_key=True)
    user_level: Mapped[KpiLevelsOrm] = mapped_column(SqlEnum(KpiLevelsOrm))
    salary_percentage: Mapped[float] = mapped_column(Float, default=0.0)

    user: Mapped["UserOrm"] = relationship("UserOrm", back_populates="kpi")


class СallOrm(BaseModelOrm):
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
    transcription: Mapped[str] = mapped_column(
        String, default="no transcription")
    file_id: Mapped[str] = mapped_column(ForeignKey(FileOrm.id))

    user: Mapped["UserOrm"] = relationship("UserOrm", back_populates="calls")
    file: Mapped["FileOrm"] = relationship("FileOrm")
