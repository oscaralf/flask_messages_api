# Messages API

## Installation


## Usage


### List messages for user <user_name>

**Definition**

`GET /user/<user_name>/messages`

Will only return new posted messages

In order to see all messages use

`GET /user/<user_name>/messages?get_old_messages=true`

**Response**

- `200 OK` on success

```json
[
    {
        "sender": "dave",
        "text": "some message",
        "target": "<user_name>",
        "id": 2,
        "sent_time": "2020-09-07T23:42:26.448303"
    },
    {
        "sender": "michael",
        "text": "another message",
        "target": "<user_name>",
        "id": 3,
        "sent_time": "2020-09-08T23:50:48.748670"
    }
]
```

### Post a new message to user <user_name>

**Definition**

`POST /user/<user_name>/messages?get_old_messages=true`

**Request**

content-type: application/json

Body data should be a json object with the following fields

- `"user_id":string` the user name of the sender (future version will get this value from authentication user)
- `"text":string` message text

Ex:
```json
{
    "user_id": "dave",
    "text": "some text 2"
}
```

**Response**

- `200 OK` on success

```json
{
    "sender": "dave",
    "text": "some text 2",
    "target": "<user_name>",
    "id": 4,
    "sent_time": "2020-09-08T01:27:14.459730"
}
```

### Delete one message for user <user_name>

**Definition**

`DELETE /user/<user_name>/messages/<message_id>`

Sending a delete with an id for an non existing message will also return status code `200 OK`, 
but 'delete_count' on the response JSON object will have '0'

**Response**

- `200 OK` on success

```json
{
    "delete_count": 1
}
```

### Delete multiple messages for user <user_name>

**Definition**

`DELETE /user/<user_name>/messages`

**Request**

content-type: application/json

Body data should be a list containing the message ids to be deleted.
The response will reflect how many where actually deleted on "delete_count"

Ex:
```json
[ 2, 4, 7 ]
```

**Response**

- `200 OK` on success

```json
{
    "delete_count": 3
}
```

### Dev notes
- Source user_id should come from the header and not from the request JSON data, and it should match the authenticated user id, this should be changed when adding authentication
- Consider GUID as identifiers to control the creation of IDs and guarantee that they don't clash between multiple instances running the REST API

