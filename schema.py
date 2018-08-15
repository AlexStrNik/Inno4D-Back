import graphene
import geojson
import json
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from models import db_session, User as UserModel, Message as MessageModel
from graphene import relay
import utils
from datetime import datetime
# -> https://github.com/graphql-python/graphene-sqlalchemy/blob/master/docs/tutorial.rst

GeoJson = json.load(open('buildings.geojson', encoding='utf-8'))
OSM_ID_2_BUILDING = {}
# -> тоже самое но id_house

for bld_f in GeoJson['features']:
    bld = bld_f
    osm_id = bld['properties']['OSM_ID']
    OSM_ID_2_BUILDING[osm_id] = bld


class Geometry(graphene.ObjectType):
    type = graphene.String(required=False)
    coordinates = graphene.List(graphene.List(graphene.List(graphene.List(graphene.Float))))

    def resolve_coordinates(self, info):
        return self['coordinates']

    def resolve_type(self, info):
        return self['type']


class Building(graphene.ObjectType):
    osm_id = graphene.Float(required=True)
    house_number = graphene.String(required=False)
    b_levels = graphene.String(required=False)
    name = graphene.String(required=False)
    street = graphene.String(required=False)
    year = graphene.Int(required=False)
    construct = graphene.Int(required=False)
    spaces = graphene.Int(required=False)
    area = graphene.Int(required=False)
    geometry = graphene.Field(lambda: Geometry)

    def resolve_geometry(self, info):
        return self['geometry']

    def resolve_osm_id(self, info):
        return self['properties']['OSM_ID']

    def resolve_house_number(self, info):
        return self['properties']['A_HSNMBR']

    def resolve_b_levels(self, info):
        return self['properties']['B_LEVELS']

    def resolve_name(self, info):
        return self['properties']['NAME']

    def resolve_area(self, info):
        return self['properties']['AREA']

    def resolve_spaces(self, info):
        return self['properties']['SPACES']

    def resolve_construct(self, info):
        return self['properties']['CONSTRUCT']

    def resolve_year(self, info):
        return self['properties']['YEAR']

    def resolve_street(self, info):
        return self['properties']['STREET']


class User(SQLAlchemyObjectType):

    user_id = graphene.Int(source='id')
    user_messages = graphene.List(lambda: Message)

    class Meta:
        model = UserModel
        interfaces = (relay.Node, )

    def resolve_user_id(self, info):
        return self.id
        
    def resolve_user_messages(self, info):
        query = Message.get_query(info)
        return query.filter(self.id == MessageModel.user_id).all()


class UserConnection(relay.Connection):
    class Meta:
        node = User                                   


class Message(SQLAlchemyObjectType):
    message_id = graphene.Int(source='id')

    class Meta:
        model = MessageModel
        interfaces = (relay.Node, )

    def resolve_message_id(self, info):
        return self.message_id


class MessageConnection(relay.Connection):
    class Meta:
        node = Message


class Query(graphene.ObjectType):
    node = relay.Node.Field()

    all_buildings = graphene.List(lambda: Building)
    building_by_id = graphene.Field(Building, required=True, osm_id=graphene.Float(required=True))                
    
    all_users = graphene.List(User)
    all_messages = graphene.List(Message)

    def resolve_all_users(self, context, **kwargs):
        user_query = User.get_query(context)
        return user_query

    def resolve_all_messages(self, context, **kwargs):
        message_query = Message.get_query(context)
        return message_query

    def resolve_building_by_id(self, info, osm_id):
        return OSM_ID_2_BUILDING[osm_id]

    def resolve_all_buildings(self, info):
        ab = []
        for k in OSM_ID_2_BUILDING:
            ab.append(OSM_ID_2_BUILDING[k])
        print(ab)
        return ab


class UserAttribute:
    first_name = graphene.String(description='First Name of the person.')
    second_name = graphene.String(description='Second_Name of the person.')
    

class CreateUserInput(graphene.InputObjectType, UserAttribute):
    pass

class CreateUser(graphene.Mutation):
    user = graphene.Field(lambda: User, description="User created by this mutation.")
    class Arguments:
        input = CreateUserInput(required=True)
        
    def mutate(self, info, input):
        data = utils.input_to_dictionary(input)
        user = UserModel(**data)
        db_session.add(user)
        db_session.commit()
    return CreateUser(user=user)    
        

class MessageAttribute:
    text = graphene.String(description='Text of the message')
    user_id = graphene.ID(description='User ID')
    reply_message_id = graphene.ID(description='Reply message ID')
    date = graphene.Date(description='Date of the Message')


class CreateMessageInput(graphene.InputObjectType, MessageAttribute):
    pass


class SendMessage(graphene.Mutation):
    message = graphene.Field(lambda: Message, description='Message created by this mutation.')

    class Arguments:
        input = CreateMessageInput(required=True)
    
    def mutate(self, info, input):
        data = utils.input_to_dictionary(input)
        data['date'] = datetime.utcnow()

        message = MessageModel(**data)
        db_session.add(message)
        db_session.commit()

        return SendMessage(message = message)            
    

class Mutation:
    send_message = SendMessage.Field()
    create_user = CreateUser.Field()    


schema = graphene.Schema(query=Query, mutation=Mutation)
# -: https://github.com/alexisrolland/flask-graphene-sqlalchemy/wiki/Flask-Graphene-SQLAlchemy-Tutorial#add-graphql-mutations
