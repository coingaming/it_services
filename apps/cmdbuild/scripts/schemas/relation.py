from marshmallow import Schema, fields


class RelationSchema(Schema):
    _type = fields.String() #":"ServiceAdminService",
    _destinationId = fields.String() #":"555012",
    _destinationType = fields.String() #":"TechnicalService",
    _sourceType = fields.String() #":"InternalEmployee",
    _sourceId = fields.String() #":531212,
    _is_direct = fields.String() #":true,
    _destinationDescription = fields.String() #":"",
    _destinationCode = fields.String() #":""