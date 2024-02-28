from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Text

class Base(DeclarativeBase):
    pass


class homework(Base):
    __tablename__ = 'homework'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subject: Mapped[int] = mapped_column(Text(300))
    task: Mapped[str] = mapped_column(Text(500))
    group: Mapped[str] = mapped_column(Text(10))
    ContentType: Mapped[str] = mapped_column(Text(30))
    Caption : Mapped[str] = mapped_column(Text(30))


class combo(Base):
    __tablename__ = 'combo'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    compound: Mapped[int] = mapped_column(Text(1000))


class usertable(Base):
    __tablename__ = 'UserInfo'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(Text(32))
    chat_id: Mapped[str] = mapped_column(Text(100))
    group: Mapped[str] = mapped_column(Text(10))
    login: Mapped[str] = mapped_column(Text(6))
    password: Mapped[str] = mapped_column(Text(30))
    key: Mapped[str] = mapped_column(Text(200))
    
    
