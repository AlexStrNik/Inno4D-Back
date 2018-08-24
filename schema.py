import graphene
import geojson
import json
import graphene
from JSON import JSON
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from models import db_session, User as UserModel, Message as MessageModel
from graphene import relay
from graphene.types import generic
import utils
import datetime
import collections
from werkzeug.security import safe_str_cmp
import json
import hashlib
from flask_graphql_auth import *
# -> https://github.com/graphql-python/graphene-sqlalchemy/blob/master/docs/tutorial.rs

def only_admin(func_dec):
    def filter_admin(_self, _info, input):
        user_query = User.get_query(_info)
        user = user_query.filter(UserModel.id == get_jwt_identity()).first()
        if(user.is_admin):
            return func_dec(_self, _info, input)
        else:
             raise GraphQLError('You are not admin')
    return filter_admin


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

GeoJson = json.load(open('buildings1.geojson', encoding='utf-8'))
OSM_ID_2_BUILDING = {}
# -> тоже самое но id_house

for bld_f in GeoJson['features']:
    bld = bld_f
    osm_id = bld['properties']['OSM_ID']
    OSM_ID_2_BUILDING[osm_id] = bld

class Geometry(graphene.ObjectType):
    type = graphene.String(required=False)
    coordinates = graphene.Field(lambda: generic.GenericScalar)

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

GeoJson_commerce = json.load(open('commerce1.geojson', encoding='utf-8'))
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
    area = graphene.Int(required=False)
    id_house = graphene.Float(required=False)
    geometry = graphene.Field(lambda: Geometry)

    def resolve_id(self, info):
        return SafeDict(self['properties'])['id']

    def resolve_area(self, info):
        return SafeDict(self['properties'])['square']

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
    
    def resolve_geometry(self, info):
        return self['geometry']

class User(SQLAlchemyObjectType):

    user_id = graphene.Int(source='id')
    user_messages = graphene.List(lambda: Message)

    class Meta:
        model = UserModel
        exclude_fields = ('password')
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
    all_buildings = graphene.List(lambda: Building)
    building_by_id = graphene.Field(Building, required=True, osm_id=graphene.Float(required=True))                
    buildings_json = graphene.Field(lambda: generic.GenericScalar)
    commerce_json = graphene.Field(lambda: generic.GenericScalar)
    all_commerce = graphene.List(lambda: Commerce)
    commerce_by_id = graphene.Field(Commerce, required=True, id=graphene.Int(required=True))

    all_users = graphene.List(User)
    all_messages = graphene.List(Message)

    protected = graphene.String(token=graphene.String())
    my_user = graphene.Field(lambda: User, token=graphene.String())

    @jwt_required
    def resolve_protected(self, context, **kwargs):
        print(get_jwt_identity())
        return("qqqq")

    @jwt_required
    def resolve_my_user(self, context, **kwargs):
        user_query = User.get_query(context)
        print(get_jwt_identity())
        user = user_query.filter(UserModel.id == get_jwt_identity()).first()
        return user

    def resolve_commerce_json(self, args):
        return GeoJson_commerce

    def resolve_buildings_json(self, args):
        return GeoJson

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

class GeometryAttribute:
    type = graphene.String(required=False)
    coordinates = graphene.Field(lambda: generic.GenericScalar)

class GeometryInput(graphene.InputObjectType, GeometryAttribute):
    pass

class CreateCommerceAttribute:
    type = graphene.String(required=True)
    status = graphene.String(required=True)
    rental_rate = graphene.Int(required=True)
    address = graphene.String(required=True)
    name = graphene.String( required=True)
    p = graphene.Int(required=True)
    id_house = graphene.Float(required=True)
    geometry = graphene.Field(lambda: GeometryInput, required=True)

class EditCommerceAttribute:
    id = graphene.Int(required=True)
    Type = graphene.String(required=False)
    status = graphene.String(required=False)
    rental_rate = graphene.Int(required=False)
    address = graphene.String(required=False)
    Name = graphene.String( required=False)
    P = graphene.Int(required=False)
    area = graphene.Int(required=False)
    id_house = graphene.Float(required=False)
    geometry = graphene.Field(lambda: GeometryInput, required=False)

class CreateCommerceInput(graphene.InputObjectType, CreateCommerceAttribute):
    pass


class EditCommerceInput(graphene.InputObjectType, EditCommerceAttribute):
    pass

class CreateCommerce(graphene.Mutation):
    commerce = graphene.Field(lambda: Commerce, description="Commerce created by this mutation.")
    class Arguments:
        input = CreateCommerceInput(required=True)
        token = graphene.String()

    @jwt_required
    @only_admin
    def mutate(self, info, input):
        data = input
        now_id = sorted(list(ID_COMMERCE.keys()))[-1]
        kek = {}
        kek["type"] = "Feature"
        properties = dict()
        properties["id"] = now_id
        properties["Name"] = data.name
        properties["Type"] = data.type
        properties["square"] = data.area
        properties["status"] = data.status
        properties["rental_rate"] = data.rental_rate
        properties["address"] = data.address
        properties["P"] = data.p
        properties["id_house"] = data.id_house
        kek["geometry"] = {
            "type": "Polygon",
            "coordinates": [data.geometry["coordinates"]]
        }
        kek["properties"] = properties
        ID_COMMERCE[now_id] = kek
        if(OSM_ID_2_COMMERCE_LIST.get(kek['properties']['id_house'], None) == None):
            OSM_ID_2_COMMERCE_LIST[kek['properties']['id_house']] = []
        OSM_ID_2_COMMERCE_LIST[kek['properties']['id_house']].append(kek['properties']['id'])
       # inp_com = open("commerce_copy.geojson", 'r', encoding="utf-8")
       # a = inp_com.readlines()
       # b = a[:len(a) - 2]
        #b[-1] = b[-1] + ','
        #kek_json = json.dumps(kek)
        #b.append(kek_json)
        #print(kek_json)
        #b.append(']')
        #b.append('}')
       # out_com = open("commerce_copy.geojson", 'w', encoding="utf-8")
     #   out_com.writelines(b)
        return CreateCommerce(commerce=kek)


        

class EditCommerce(graphene.Mutation):
    commerce = graphene.Field(lambda: Commerce, description="Commerce edited by this mutation.")
    class Arguments:
        input = EditCommerceInput(required=True)
        token = graphene.String()
    
    @jwt_required
    @only_admin
    def mutate(self, info, input):
        data = input
        print(data)
        house = data.id_house
        com = ID_COMMERCE[data.id]['properties']
        was = ID_COMMERCE[data.id]['properties']['id_house']
        for i in data:
            print(i)
            com[i] = data[i]
        ID_COMMERCE[data.id]['properties'] = com
        if was != house:
            del OSM_ID_2_COMMERCE_LIST[was][data.id]
            if OSM_ID_2_COMMERCE_LIST.get(house, None) == None:
                OSM_ID_2_COMMERCE_LIST[house] = []
            OSM_ID_2_COMMERCE_LIST[house].append(data.id)
    

        return EditCommerce(commerce=ID_COMMERCE[data.id]) 

class CreateUserAttribute:
    first_name = graphene.String(description='First Name of the person.')
    second_name = graphene.String(description='Second Name of the person.')
    # post = graphene.String(description='Post of the person.')
    login = graphene.String(description='LOGIN')
    password = graphene.String(description='PAROL')

class EditUserAttribute:
    id = graphene.Int(descripton='Id of the person.', required=True)
    first_name = graphene.String(description='First Name of the person.')
    second_name = graphene.String(description='Second Name of the person.')
    password = graphene.String(description='Password of the person.')
    is_new_user = graphene.Boolean()

class CreateUserInput(graphene.InputObjectType, CreateUserAttribute):
    pass


class EditUserInput(graphene.InputObjectType, EditUserAttribute):
    pass

class CreateUser(graphene.Mutation):
    user = graphene.Field(lambda: User, description="User created by this mutation.")
    class Arguments:
        input = CreateUserInput(required=True)
        
    def mutate(self, info, input):
        data = input
        data['password'] = hashlib.blake2b(data.password.encode('utf-8')).hexdigest()
        data['is_new_user'] = True
        user = UserModel(**data)
        db_session.add(user)
        db_session.commit()
        
        return CreateUser(user=user)    
        

class EditUser(graphene.Mutation):
    user = graphene.Field(lambda: User, description="User edited by this mutation.")
    class Arguments:
        token = graphene.String()  
        input = EditUserInput(required=True)
    
    @jwt_required
    def mutate(self, info, input):
        data = input
        query = User.get_query(info)
        id = input.id
        del input['id']
        print(get_jwt_identity(), id)
        if(id != get_jwt_identity()):
             raise GraphQLError('Incorrect user id')
        query.filter(UserModel.id == input.id).update({**input})
        db_session.commit()

        return EditUser(query.filter(UserModel.id == input.id).first())

class MessageAttribute:
    text = graphene.String(description='Text of the message')
    user_id = graphene.Int(description='User ID')
    reply_message_id = graphene.Int(description='Reply message ID', required=False)
    date = graphene.Date(description='Date of the Message')


class CreateMessageInput(graphene.InputObjectType, MessageAttribute):
    pass


class SendMessage(graphene.Mutation):
    message = graphene.Field(lambda: Message, description='Message created by this mutation.')

    class Arguments:
        input = CreateMessageInput(required=True)
    
    def mutate(self, info, input):
        data = input
        data['date'] = datetime.datetime.utcnow()

        message = MessageModel(**data)
        db_session.add(message)
        db_session.commit()

        return SendMessage(message = message)            
    
class AuthMutation(graphene.Mutation):
    class Arguments(object):
        username = graphene.String()
        password = graphene.String()

    access_token = graphene.String()
    refresh_token = graphene.String()

    def mutate(self, info, username, password):
        query = db_session.query(UserModel)
        password = hashlib.blake2b(password.encode('utf-8')).hexdigest()
        user = query.filter(username == UserModel.login).first()
        if user:
            if safe_str_cmp(user.password, password):
                return AuthMutation(access_token=create_access_token(user.id), refresh_token=create_refresh_token(username))
        else:
            new_user = UserModel(login=username, password=password, is_new_user=True, is_admin=False)
            db_session.add(new_user)
            db_session.commit()
            return AuthMutation(access_token=create_access_token(new_user.id), refresh_token=create_refresh_token(username))
        raise GraphQLError('Incorrect login or password')

class RefreshMutation(graphene.Mutation):
    class Arguments(object):
        token = graphene.String()

    new_token = graphene.String()

    @jwt_refresh_token_required
    def mutate(self, info):
        current_user = get_jwt_identity()
        return RefreshMutation(new_token=create_access_token(identity=current_user))


class Mutation(graphene.ObjectType):
    auth_user = AuthMutation.Field()
    refresh_user = RefreshMutation.Field()
    send_message = SendMessage.Field()
    edit_user = EditUser.Field()
    create_user = CreateUser.Field()
    create_commerce = CreateCommerce.Field()
    edit_commrece = EditCommerce.Field()

class Subscription(graphene.ObjectType):
    messages = SQLAlchemyConnectionField(Message)

    # mutation oject that was published will be passed as
    # root_value of subscription
    def resolve_messages(self, info):
        pass
        
schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)
# -: https://github.com/alexisrolland/flask-graphene-sqlalchemy/wiki/Flask-Graphene-SQLAlchemy-Tutorial#add-graphql-mutations
