from scripts.schemas.card import InternalEmployeeCardSchema



class InternalEmployee:
    
    schema = InternalEmployeeCardSchema

    __slot__ = (
        'Code'
        'Description'
        'Notes'
        'Number'
        'LastName'
        'FirstName'
        'Email'
        'Mobile'
        'Phone'
        'State'
        'ContractStart'
        'ContractEnd'
        'Company'
        'Type'
    )

    def __init__(
        self,
        code: str,
        description: str,
        notes: str,
        number: str,
        lastName: str,
        firstName: str,
        email: str,
        mobile: str,
        phone: str,
        state: str,
        contractStart: str,
        contractEnd: str,
        company: str,
        employee_type: str
    ):
        self.Code = code
        self.Description = description
        self.Notes = notes
        self.Number = number
        self.LastName = lastName
        self.FirstName = firstName
        self.Email = email
        self.Mobile = mobile
        self.Phone = phone
        self.State = state
        self.ContractStart = contractStart
        self.ContractEnd = contractEnd
        self.Company = company
        self.Type = employee_type



class Service:
    pass