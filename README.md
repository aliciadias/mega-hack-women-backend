## Flask login, SQLite/SQLAchlemy DB and SocketIO chat

The following project is part of the Mega Hack Women 2020 marathon, a hackathon dedicated only to women, which took place between 30 August and 7 September 2020. It contains the backend of the empreenDelas paltaform.

## Installing
To install, run the following codes after cloning the repository.

    virtualenv env -p python3
    source env/bin/activate
    (env) pip install -r requirements.txt
Then run with:

    (env) python3 api.py
It should run on `http://127.0.0.1:5000/` unless otherwise specified.

## Documentation and Useful resources

Subscrition:

    route: /api/users
    method: POST
    payload: "name", "password", "email", "formal", "business", "area"
    RETURN: email

To get a **token** and facilitate the auth process:

    route: /api/token/<string:email>
    method: GET
    AUTH: email:password
    RETURN: id, token
To see the get the current user **profile**:

    route: /api/users/<int:id>
    AUTH: token:x
    RETURNS: name, business, area, description, email, formal
To **edit** the user's profile:

    route:/api/profile/edit/<int:id>
    method: PUT
    AUTH: token:x
    payload: id, description
    RETURNS:id, description
To get a **manual match**:

    route: /api/profile/all_users
    method: GET
    AUTH: token:x
    RETURNS: name, description, email, formal, business, area <<-- ALL USERS
**OR**:

    route: /api/profile/filter_users
    method: PUT
    AUTH: token:x
    payload: "business"**, "area"** (**If no value == null)
    RETURNS: name, description, email, formal, business, area <<-- ALL USERS

To get the **smart match** feature:

    route: /api/profile/full_match/<int:id>
    method: PUT
    AUTH: token:x
    RETORNA: name, description, email, formal, business, area <<-- 0 to 3 USERS
To get the **user's email** (to be deprecated after the chat is running)

    route: /api/user_email/<int:id>
    method: GET
    AUTH: token:x
    RETURNS: email

## Examples
In this `curl` command we register an user named `simple` with a password `flask`, an sample email `test@test.com`, formal status as `True`, business as `selling`and area as `clothes`.

Note the `Location` value gives you the user's profile page with it's database ID. 
   

    curl -i -X POST -H "Content-Type: application/json" -d '{"name": "simple", "password":"flask", "email":"test@test.com", "formal":true, "business":"selling", "area":"clothes"}' http://127.0.0.1:5000/api/users
        HTTP/1.0 201 CREATED
        Content-Type: application/json
        Content-Length: 26
        Location: http://127.0.0.1:5000/api/users/2
        Access-Control-Allow-Origin: *
        Server: Werkzeug/1.0.1 Python/3.8.2
        Date: Tue, 08 Sep 2020 00:37:46 GMT
        
        {"email":"test@test.com"}
Next we want to test our login on a **protected route**:

    curl -u test@test.com:flask -i -X GET http://127.0.0.1:5000/api/users/2
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 105
    Access-Control-Allow-Origin: *
    Server: Werkzeug/1.0.1 Python/3.8.2
    Date: Tue, 08 Sep 2020 00:44:28 GMT
    
    {"area":"clothes","business":"selling","desc":null,"formal":true,"id":2,"name":"simple","schedule":null}

We should also get a token to make login simpler:

    curl -u test@test.com:flask -i -X GET http://127.0.0.1:5000/api/token/test@test.com
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 163
    Access-Control-Allow-Origin: *
    Server: Werkzeug/1.0.1 Python/3.8.2
    Date: Tue, 08 Sep 2020 00:46:28 GMT
    
    {"duration":600000,"id":2,"token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MiwiZXhwIjoxNjAwMTI1OTg4LjYzNDEyMjh9.bUioStCRa1S7_oz7byVF7mnZXuvCE7K0yzu0xooyN3k"}
    
Note the duration of our token is in *seconds*.


Smart Match example:

    curl -u eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MiwiZXhwIjoxNjAwMTI1OTg4LjYzNDEyMjh9.bUioStCRa1S7_oz7byVF7mnZXuvCE7K0yzu0xooyN3k:x -i -X PUT -H "Content-Type: application/json" -d '{"data":{"business":null, "area":null}}' http://127.0.0.1:5000/api/full_match/2
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 70
    Access-Control-Allow-Origin: *
    Server: Werkzeug/1.0.1 Python/3.8.2
    Date: Tue, 08 Sep 2020 00:57:55 GMT
    
    [{"area":"front","business":"ti","desc":null,"id":1,"name":"simple"}]
Note the *token:x* format, "x" is an random password value and it will be ignored on the backend. Also note the dict of dict format, that's how the API expects to receive your request.

## Chat
Coming soon...

## Front-End
The front-end for this plataform can be found at this [repository](https://github.com/lzcee/mega-hack-women)
