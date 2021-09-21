## Coybot 2 

It is the new and improved version of coybot

## Set up

Install dependencies with `pip install -r requirements.txt`

Create a file in cogs called secret.py, and put:

```
token = <discord token>
game_servers = [
    {
        'discord_channel_id' : <Array of Channel to put here>,
        'game_server_ip' : 'Game server ip',
        'port': 123,
        'password': 'password'
    }
]
```