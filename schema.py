import graphene
import geojson
import json
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from models import db_session, User as UserModel, Message as MessageModel
from graphene import relay
import utils
from datetime import datetime
import collections
# -> https://github.com/graphql-python/graphene-sqlalchemy/blob/master/docs/tutorial.rst

class SafeDict(collections.MutableMapping):

    def __init__(self, dict):
        self.store = dict  # use the free update to set keys

    def __getitem__(self, key):
        return self.store.get(key, None)

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

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
    commercies = graphene.List(lambda: Commerce)
    area = graphene.Int(required=False)
    geometry = graphene.Field(lambda: Geometry)

    def resolve_geometry(self, info):
        return self['geometry']

    def resolve_osm_id(self, info):
        return SafeDict(self['properties'])['OSM_ID']

    def resolve_house_number(self, info):
        return SafeDict(self['properties'])['A_HSNMBR']

    def resolve_b_levels(self, info):
        return SafeDict(self['properties'])['B_LEVELS']

    def resolve_name(self, info):
        return SafeDict(self['properties'])['NAME']

    def resolve_area(self, info):
        return SafeDict(self['properties'])['AREA']

    def resolve_spaces(self, info):
        return SafeDict(self['properties'])['SPACES']

    def resolve_construct(self, info):
        return SafeDict(self['properties'])['CONSTRUCT']

    def resolve_year(self, info):
        return SafeDict(self['properties'])['YEAR']

    def resolve_commercies(self, info):
        id = int(SafeDict(self['properties'])['OSM_ID'])
        if(OSM_ID_2_COMMERCE_LIST.get(id, None) != None):
            return list(map(lambda v: ID_COMMERCE[v], OSM_ID_2_COMMERCE_LIST[id]))
        return []

    def resolve_street(self, info):
        return SafeDict(self['properties'])['STREET']

GeoJson_commerce = json.load(open('commerce.geojson', encoding='utf-8'))
ID_COMMERCE = {}
OSM_ID_2_COMMERCE_LIST = {}

for com in GeoJson_commerce['features']:
    id_com = com['properties']['id']
    ID_COMMERCE[id_com] = com
    if(OSM_ID_2_COMMERCE_LIST.get(com['properties']['id_house'], None) == None):
        OSM_ID_2_COMMERCE_LIST[com['properties']['id_house']] = []
    OSM_ID_2_COMMERCE_LIST[com['properties']['id_house']].append(com['properties']['id'])

print(OSM_ID_2_COMMERCE_LIST)

class Commerce(graphene.ObjectType):
    id = graphene.Int(required=True)
    type = graphene.String(required=False)
    status = graphene.String(required=False)
    rental_rate = graphene.Int(required=False)
    address = graphene.String(required=False)
    name = graphene.String(required=False)
    p = graphene.Int(required=False)
    id_house = graphene.Float(required=False)

    def resolve_id(self, info):
        return SafeDict(self['properties'])['id']

    def resolve_type(self, info):
        return SafeDict(self['properties'])['Type']

    def resolve_status(self, info):
        return SafeDict(self['properties'])['status']

    def resolve_rental_rate(self, info):
        return SafeDict(self['properties'])['rental_rate']
        
    def resolve_address(self, info):
        return SafeDict(self['properties'])['address']
    
    def resolve_name(self, info):
        return SafeDict(self['properties'])['Name']
    
    def resolve_p(self, info):
        return SafeDict(self['properties'])['P']
    
    def resolve_id_house(self, info):
        return SafeDict(self['properties'])['id_house']

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
    
    all_commerce = graphene.List(lambda: Commerce)
    commerce_by_id = graphene.Field(Commerce, required=True, id=graphene.Int(required=True))

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
            ab.append(SafeDict(OSM_ID_2_BUILDING[k]))
        print(ab)
        return ab
    
    def resolve_commerce_by_id(self, inf, id):
        return ID_COMMERCE[id]

    def resolve_all_commerce(self, info):
        ab = []
        for k in ID_COMMERCE:
            ab.append(SafeDict(ID_COMMERCE[k]))
        print(ab)
        return ab


class UserAttribute:
    first_name = graphene.String(description='First Name of the person.')
    second_name = graphene.String(description='Second Name of the person.')
    

class CreateUserInput(graphene.InputObjectType, UserAttribute):
    pass

class CreateUser(graphene.Mutation):
    user = graphene.Field(lambda: User, description="User created by this mutation.")
    class Arguments:
        input = CreateUserInput(required=True)
        
    def mutate(self, info, input):
        data = input
        user = UserModel(**data)
        db_session.add(user)
        db_session.commit()
        
        return CreateUser(user=user)    
        

class MessageAttribute:
    text = graphene.String(description='Text of the message')
    user_id = graphene.Int(description='User ID')
    reply_message_id = graphene.Int(description='Reply message ID', required=False)
    # date = graphene.Date(description='Date of the Message')


class CreateMessageInput(graphene.InputObjectType, MessageAttribute):
    pass


class SendMessage(graphene.Mutation):
    message = graphene.Field(lambda: Message, description='Message created by this mutation.')

    class Arguments:
        input = CreateMessageInput(required=True)
    
    def mutate(self, info, input):
        data = input
            # data['date'] = datetime.utcnow()

        message = MessageModel(**data)
        db_session.add(message)
        db_session.commit()

        return SendMessage(message = message)            
    

class Mutation(graphene.ObjectType):
    send_message = SendMessage.Field()
    create_user = CreateUser.Field()    


schema = graphene.Schema(query=Query, mutation=Mutation)
# -: https://github.com/alexisrolland/flask-graphene-sqlalchemy/wiki/Flask-Graphene-SQLAlchemy-Tutorial#add-graphql-mutations
