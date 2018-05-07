The interface has been created to handle REST queries which support few tasks of GET and DELETE. A sample query with authentication are below.

This url is used to get full details of a game of developer
```
http --auth username:password https://protected-fortress-58577.herokuapp.com/rest_view/8
```

or to delete a game, use the following link

```
http --auth username:password DELETE https://protected-fortress-58577.herokuapp.com/rest_view/8
```

or to view games, use the following link

```
http https://protected-fortress-58577.herokuapp.com/rest_view
```
or use the following link to view the games of a developer who is identified through the credential provided

```
http --auth username:password https://protected-fortress-58577.herokuapp.com/rest_view
```

REST interface can be used to retrieve games for guest user and registered user.
Registered user needs to provide his credentials to delete game or view complete details of game
Guest user (without authentication) can see all games or selected games but only limited details


