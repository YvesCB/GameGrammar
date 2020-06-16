# GameGrammar Twitch Bot

A repo for the GameGrammar Twitch bot and other projects down the line.

## How to run

1. Clone the repo
2. `pip install -r requirements.txt`
3. Copy the example config file with `cp config_example.py config.py`
4. Set up your IRC connection data in `config.py`
5. Set up the list of superadmins in `config.py`
6. Run the bot with `python yvesbot.py`

That's it! :)

## Commands

### `!test`

A command for testing which prints out the requesting user's name.

### `!j <term> [<result_number>]`

Returns the jisho.org entires for `<term>`. Example: `!j 関係`.
This is limited to three meanings.

This command can also take a number at the end. Example: `!j 関係 2`.
This would return the second result for “関係”.

### `!tags`

Will show the list of all availalbe tags.

### `!add_tag <tag_name> <tag_response>`

Adds a tag to the database. A tag is kind of command, triggered when a user writes `!<tag_name>`,
causing the bot to reply with `tag_response`. An example:

```
!add_tag hello Hi guys!
> Tag hello added.
!hello
> Hi guys!
```

Added commands are stored persistently in the database and come into effect immediately.
This command is restricted to mods.

### `!remove_tag <tag_name>`

Analogously to `!add_tag`, this command removes a tag from the database, which comes into
effect immediately. This command is restricted to mods.

### `!<tag_name>`

If `tag_name` is a tag in the database, using it as a command will cause the bot to reply with
that tag's respective `tag_response`. See `!add_tag`.

### `!mods`

Shows a list of all mods.

### `!mod <user_name>`

Adds a user to the mods table. This command is restricted to superadmins.

### `!demod <user_name>`

Removes a user from the mods table. This command is restricted to restricted to superadmins.

## Roadmap

The goal is to eventually have a bunch of features for the twitch bot and functionality that would carry over to discord as well. For now, I think the focus should be to replace the functionality of the streamlabs bot bit by bit as to not needing to rely on it anymore.

### Current tasks

* Create discord bot and link it to twitch chat bot
* Create a shoutout command
* Create an uptime command

# Discord Bot

GrammarBot will make your life better!

## How to run

1. Clone the repo
2. `pip install -r requirements.txt`
3. Copy the example config file with `cp config_example.py config.py`
4. Set up your Discord connection data in `config.py`
5. Set up the admin in `config.py`
6. Run the bot with `python yvesbot.py`

## Commands

### `!help`

Use the help command to get information about the available commands.

## Roadmap

This bot is meant to be used for all kinds of different thigns in the future. Currently, it supports some very basic things. 

### Current tasks
 
* Make the bot post automatically when the stream goes live.
* Update the help command: sort entries in a relevant way and make it context sensitive
