from marshmallow import Schema, fields


class EmployeeCardSchema(Schema):
    Code = fields.String()
    Description = fields.String()
    Notes = fields.String()
    Number = fields.String()
    LastName = fields.String()
    FirstName = fields.String()
    DisplayName = fields.String()
    JobTitle = fields.String()
    Email = fields.String()
    Mobile = fields.String()
    Phone = fields.String()
    State = fields.String() # lookup
    ContractStart = fields.String()
    ContractEnd = fields.String()
    Company = fields.String() # ref
    Type = fields.String() # lookup
    OU = fields.String() # ref
    ReportsTo = fields.Integer() # ref
    OwnerOf = fields.Integer() # ref
    IsManager = fields.String()


class OUCardSchema(Schema):
    Parent = fields.Integer() # ref
    Code = fields.String()
    Notes = fields.String()
    Description = fields.String()
    Level = fields.Integer() # lookup
    Manager = fields.Integer() # ref
    Company = fields.Integer() # ref
    Name = fields.String()


class CompanyCardSchema(Schema):
    Code = fields.String() #"YAMIA",
    Description = fields.String() #"Yamia [YAMIA]",
    Notes = fields.String() #null,
    CompanyTitle = fields.String() #"Yamia",
    Address = fields.String() #null,
    Postcode = fields.String() #null,
    City = fields.String() #"New York",
    Region = fields.String() #null,
    Country = fields.String() #5955,
    Type = fields.String() #null,
    ActivationChannel = fields.String() #null,
    Phone = fields.String() #null,
    Fax = fields.String() #null,
    Email = fields.String() #null,
    Website = fields.String() #null


class ServiceCardSchema(Schema):
    Category = fields.String() #6847,
    Name = fields.String() #"Server Maintenance and Support"
    ServiceState = fields.String() #225
    ServiceOwner = fields.String() #6087
    ServiceMasterAdmin = fields.String()
    ExtendedDescription = fields.String() #"Maintenance and support of server(s) and server related component(s)."


class ServiceCategoryCardSchema(Schema):
    Parent = fields.String() #6847,
    Code = fields.String() #: "SR 1",
    Description = fields.String() #: "test",
    State = fields.String() #: 226,
    Index = fields.String() #: "1"