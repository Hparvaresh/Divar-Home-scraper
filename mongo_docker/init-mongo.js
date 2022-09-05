db.createUser(
	{
		user  : "hamed",
		pwd   : "h123",
		roles : [
			{
				role : "dbOwner",
				db   : "default"
			}
		]
	}
)