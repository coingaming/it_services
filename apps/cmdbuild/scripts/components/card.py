from marshmallow import Schema
from scripts.schemas.card import OUCardSchema, EmployeeCardSchema, \
    CompanyCardSchema, ServiceCardSchema, ServiceCategoryCardSchema


class EmployeeCardComponent:

    schema = EmployeeCardSchema

    __slots__ = (
        'Code',
        'Description',
        'Notes',
        'Number',
        'LastName',
        'FirstName',
        'DisplayName',
        'JobTitle',
        'Email',
        'Mobile',
        'Phone',
        'State',
        'ContractStart',
        'ContractEnd',
        'Company',
        'Type',
        'OU',
        'ReportsTo',
        'OwnerOf',
        'IsManager',
    )

    def __init__(
        self,
        code: str,
        lastName: str,
        firstName: str,
        displayName: str,
        jobTitle: str,
        email: str,
        state: str, # lookup
        type: str, # lookup
        isManager: str = "false",
        contractStart: str = None,
        contractEnd: str = None,
        mobile: str = None,
        phone: str = None,
        number: str = None,
        notes: str = None,
        description: str = None,
        company: str = None, # ref
        OU: str = None, # ref
        reportsTo: str = None, # ref
        ownerOf: str = None, # ref
        ):

        self.Code = code
        self.Description = description
        self.Notes = notes
        self.Number = number
        self.LastName =lastName
        self.FirstName = firstName
        self.DisplayName = displayName
        self.JobTitle = jobTitle
        self.Email = email
        self.Mobile = mobile
        self.Phone = phone
        self.State = state
        self.ContractStart = contractStart
        self.ContractEnd = contractEnd
        self.Company = company
        self.Type = type
        self.OU = OU
        self.ReportsTo = reportsTo
        self.OwnerOf = ownerOf
        self.IsManager = isManager


class OUComponent:

    schema = OUCardSchema

    __slots__ = (
        'Parent',
        'Code',
        'Notes',
        'Description',
        'Level',
        'Manager',
        'Company',
        'Name',
    )

    def __init__(
        self,
        name: str,
        description: str,
        code: str = None,
        parent: str = None,
        notes: str = None,
        level: int = None,
        manager: int = None,
        company: int = None,
        ):

        self.Parent = parent
        self.Code = code
        self.Notes = notes
        self.Description = description
        self.Level = level
        self.Manager = manager
        self.Company = company
        self.Name = name


class CompanyComponent:

    schema = CompanyCardSchema

    __slots__ = (
        'Code',
        'Description',
        'Notes',
        'CompanyTitle',
        'Address',
        'Postcode',
        'City',
        'Region',
        'Country',
        'Type',
        'ActivationChannel',
        'Phone',
        'Fax',
        'Email',
        'Website'
    )

    def __init__(
        self,
        companyTitle: str,
        code: str = None,
        description: str = None,
        notes: str = None,        
        address: str = None,
        postcode: str = None,
        city: str = None,
        region: str = None,
        country: str = None,
        type: str = None,
        activationChannel: str = None,
        phone: str = None,
        fax: str = None,
        email: str = None,
        website: str = None
    ):
        self.Code = code
        self.Description = description
        self.Notes = notes
        self.CompanyTitle = companyTitle
        self.Address = address
        self.Postcode = postcode
        self.City = city
        self.Region = region
        self.Country = country
        self.Type = type
        self.ActivationChannel = activationChannel
        self.Phone = phone
        self.Fax = fax
        self.Email = email
        self.Website = website


class ServiceComponent:
    
    schema = ServiceCardSchema

    __slots__ = (
        'Category',
        'Name',
        'ServiceState',
        'ServiceOwner',
        'ExtendedDescription',
    )

    def __init__(
        self,
        category: str,
        name: str,
        service_state: str,
        service_owner: str,
        extended_description: str
    ):

        self.Category = category
        self.Name = name
        self.ServiceState = service_state
        self.ServiceOwner = service_owner
        self.ExtendedDescription = extended_description


class ServiceCategoryComponent:
    
    schema = ServiceCategoryCardSchema

    __slots__ = (
        'Parent',
        'Code',
        'Description',
        'State',
        'Index',
    )

    def __init__(
        self,
        parent: str,
        code: str,
        description: str,
        state: str,
        index: str
    ):
        self.Parent = parent
        self.Code = code
        self.Description = description
        self.State = state
        self.Index = index