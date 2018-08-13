import graphene
import geojson
import json

GeoJson = json.load(open('buildings.geojson', encoding='utf-8'))
OSM_ID_2_BUILDING = {}

for bld_f in GeoJson['features']:
    bld = bld_f['properties']
    osm_id = bld['OSM_ID']
    OSM_ID_2_BUILDING[osm_id] = bld


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

    def resolve_osm_id(self, info):
        return self['OSM_ID']

    def resolve_house_number(self, info):
        return self['A_HSNMBR']

    def resolve_b_levels(self, info):
        return self['B_LEVELS']

    def resolve_name(self, info):
        return self['NAME']

    def resolve_area(self, info):
        return self['AREA']

    def resolve_spaces(self, info):
        return self['SPACES']

    def resolve_construct(self, info):
        return self['CONSTRUCT']

    def resolve_year(self, info):
        return self['YEAR']

    def resolve_street(self, info):
        return self['STREET']


class Query(graphene.ObjectType):
    all_buildings = graphene.List(lambda: Building)
    building_by_id = graphene.Field(Building, required=True, osm_id=graphene.Float(required=True))

    def resolve_building_by_id(self, info, osm_id):
        return OSM_ID_2_BUILDING[osm_id]

    def resolve_all_buildings(self, info):
        ab = []
        for k in OSM_ID_2_BUILDING:
            ab.append(OSM_ID_2_BUILDING[k])
        print(ab)
        return ab

schema = graphene.Schema(query=Query)
