from sqlalchemy import *
from sqlalchemy.orm import (scoped_session, sessionmaker, relationship, backref)
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql://inno4d:inno4d@localhost:5432/inno4d')
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

# -> пиши модель юзера, вот инфа
# -: http://docs.graphene-python.org/projects/sqlalchemy/en/latest/tutorial/
# -> я буду писать модель сообщения


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key = true)
    first_name = Column(String)                    
    second_name = Column(String)
            

class Message(Base):
    __tablename__ = 'message'
    id = Column(Integer, primary_key=true)
    text = Column(Text)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref='messages') # -> user.messages вернет список всех сообщений юзера
    date = Column(Date)
    reply_message_id = Column(Integer, ForeignKey('message.id'))
    reply_message = relationship('Message', remote_side=[id]) # <- что это за строчка?
    
# -> это сообщение на которое отвечает (ссылается) это сообщение
# <- это я понимаю по названию reply, a что за aremote_side?
# -> сам не знаю Ctrl-C + Ctrl-V из доков. Как я понял указывает кто главный.
# -> Ну типа из-за того что оно само на себя ссылается

# <- 10.91.38.199
# -> Пасиб
# -> вроде сработало !!
# <- Ты просто убрал reply_id?  
'''
Base.metadata.create_all(engine) # -> тестим

tolya = User(first_name='Tolya', second_name='Werner')
alex = User(first_name='Alex', second_name='Str')

hello_tolya = Message(text='Hello Tolya', user=alex)
kek = Message(text='Alex, tashi', user=tolya, reply_message=hello_tolya)
db_session.add(alex)
db_session.add(tolya)
db_session.add(hello_tolya)
db_session.add(kek)
db_session.commit()
'''
# <- мне написать функцию messages?
# -> SqlAlchemy сделает это за тебя
# <- удобно
# -> Нам нужны чаты?
# <- Всм?
# -> Группы на несколько человек. Или сделать тольку личку и общий чат
# <- Чей чат? Жителей?
# -> Чат тех кто зарегался на форуме. И кого тип пропустили. Модераторы будут банить
# <- я предлагаю чисто личку
# -> Общий нужен тоже. Там будут пожелания по развитию сайта
# <- Может просто вкладка с фидбеком?
# -> То есть просто общий чат? Где будет фидбэк и ответ на фидбэк?
# <- ладно, тогда пусть будет общий чат 
# -> зато меньше проблем)
# <- ok
# <- как будет выглядеть sql таблица?
# -> фиг его знает. SqlAlchemy должно сгенерить
# -> сейчас будем тестить. отдельно таблицы. потом подключим к graphQL