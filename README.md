# GameGrammar

A repo for the GameGrammar Twitch bot and other projects down the line.

## How to run

1. Clone the repo
2. Copy the example config file with `cp config_example.py config.py`
3. Set up your IRC connection data in `config.py`

That's it! :)

## Roadmap

The goal is to eventually have a bunch of features for the twitch bot and functionality that would carry over to discord as well. For now, I think the focus should be to replace the functionality of the streamlabs bot bit by bit as to not needing to rely on it anymore.

The first thing would be to a simply database of prewritten messages that can be called and shown in chat. Also functionality to dynamically add and remove said messages. We'll call that the tag feature

### Current tasks

* Improve Twitch bot functionality: Tag feature
* Create discord bot and link it to twitch chat bot
