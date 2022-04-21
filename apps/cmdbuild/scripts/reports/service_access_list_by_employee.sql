BEGIN
	RETURN QUERY
    SELECT InternalEmployee ."Description" as Employee,
	TechnicalService."Name" as Service, 
    AdminEmployee."Description" as ServiceAdmin,
    AdminEmployee."Email" as ServiceAdminEmail
    FROM public."InternalEmployee" as InternalEmployee
	INNER JOIN public."Map_ServiceAccessService" as Map_ServiceAccessService
	ON InternalEmployee."Id" = Map_ServiceAccessService."IdObj1"
	INNER JOIN public."TechnicalService" as TechnicalService
	ON Map_ServiceAccessService."IdObj2" = TechnicalService."Id"
	INNER JOIN public."Map_ServiceMAdminService" as Map_ServiceAdminService
	ON Map_ServiceAdminService."IdObj2" = TechnicalService."Id"
	INNER JOIN public."InternalEmployee" as AdminEmployee
	ON Map_ServiceAdminService."IdObj1" = AdminEmployee."Id"
    WHERE (CASE WHEN i_employee IS NOT null
		   THEN InternalEmployee."Id" = i_employee
		   ELSE true 
           END)
    ORDER BY ServiceAdmin;
END;