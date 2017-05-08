# greenhouse-commandline-tool
Tool to utilize the Harvest API to manipulate your Greenhouse account

Will require a Harvest API key, this is the first prompt to the user.

In Greenhouse you can manage the permissions on an API key. As new permissions are added by Greenhouse they won't automatically 
be added to your existing keys. It is best to use this tool with a key that has all permissions added.

Many actions require you to select a user to perform the action on behalf of. If that user's profile doesn't posses the permission
to perform the action in Greenhouse the action won't be able to be completed via the API either. Because of this it is best
to use a site-admin based user with all user specific permissions.

