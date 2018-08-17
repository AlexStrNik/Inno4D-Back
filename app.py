from flask import Flask

from flask_graphql import GraphQLView
from schema import schema

app = Flask(__name__)
app.debug = True

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))
# <- что за JSON.py?\
# <- и мне писать mutation для зданий и коммерции?
# -> JSON не нужен, он есть в коробке
# -> пиши mutation для зданий
# -> нужно изменение всего кроме геометрии, ид, высоты, адреса, номера дома
# -> стопа. ток для комерции. Имя тип площадь и тд
# <- то есть для зданий не надо?
# <- а вдруг там внезапно этаж сверху построят
# <- или адреса изменят
if __name__ == '__main__':
    app.run(host='0.0.0.0')

# -: tcpip 5555
# -> что будем делать?
# <- поднимем сервер и я чекну одну вещь
# -> ок
# -> готово
# <- вижу 
# -> го с помощью sqlalchemy и graphql напишем модель для "Идей и Проблем"
# -> и напишем чатик
# <- ок, го начинать?
# -> го. я ставлю
# <- ок, я пока документацию поситаю :)
# -> у нас будет Postgres, а не MySQL. Там есть списки, и он у меня установлен))
# -> SqlAlchemy умеет соединяться с ним
# -: http://docs.graphene-python.org/projects/sqlalchemy/en/latest/tutorial/