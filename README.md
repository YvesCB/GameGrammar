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

The first thing would be to a simply database of prewritten messages that can be called and shown in chat. Also functionality to dynamically add and remove said messages. We'll call that the tag feature

### Current tasks

* Improve Twitch bot functionality: Tag feature
* Create discord bot and link it to twitch chat bot

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

### `!t <name>`

Displays the tag with the name specified if it exists.

### `!tags`

Displays the list of tags availalbe.

### `!t_add <name> <content>`

**Must be used by admin.** Adds a new tag (if the name is not already taken) with the name and content specfied. 

```
!t_add hello Hello this is the hello tag.
> Successfully added tag hello.
!t hello
> Hello this is the hello tag.
```

### `!t_remove <name>`

**Must be used by admin.** Removes a tag if it exitsts.

### `!admins`

Shows you a list of the current roles that are considered admins on the server. 

### `!admin_add <name>`

**Must be used by admin.** If no admin roles are specified, only the admin account specified in config will be able to use this commmand. Adds a role on the server to the list of admin roles.

```
!admin_add Mod
> Successfully added the role Mod to the list of admins.
!admins
> The admin roles are:
> Mod
```