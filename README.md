# Bjarne 

Bjarne is a Discord server bot built for and maintained by the UWS Game Dev Society.

It is written in Python using [discord.py](https://github.com/Rapptz/discord.py), a wrapper for the Discord API.

It is currently hosted on the Heroku cloud platform.

## Contributing
If you are a member of the society and wish to add features, enhancements or fix bugs your contribution is welcome!

Feel free to choose an item on the [Issues page](https://github.com/martygrant/uwsgamedevbot/issues) section that you would like to work on. Already implemented features are [listed below](https://github.com/martygrant/uwsgamedevbot#features).

To get started you should get the example running from the [discord.py repo](https://github.com/Rapptz/discord.py) and check out the documentation there. For a more in-depth tutorial there is a really handy [Discord server](https://discord.gg/GWdhBSp) with guides for basic operations.

For developing the bot you should create your own bot and run it in your own private server to test out your functions so we can avoid a lot of bother with security tokens and the Bjarne bot being hosted in a cloud server. Once you are happy you can submit a pull request and it can be added to Bjarne.

If you have any questions for making a contribution, or a code related question for your change you can message @midnightpacific in the Discord server.

### Requirements
* Python 3.4.2+
* [discord.py](https://github.com/Rapptz/discord.py)
* [weather-api](https://pypi.org/project/weather-api/)
* [requests](https://pypi.org/project/requests/)
* [wikipedia](https://github.com/goldsmith/Wikipedia)

### Contributors
* [Medallyon](https://github.com/Medallyon)

## Features
* Automatic new member welcome message.
* !say - make Bjarne repeat a message.    
* !bjarnequote - Display a quote from Bjarne Stroupstrup, creator of C++.
* !random - Random number generator.
* !dice - Roll a 6 sided dice.
* !math - Math operations.
* !quote - Quote users in the channel, picks a random message they have sent.
* Post an "Unlimited Power" Palaptine meme when anyone mentions the word "power" - currently disabled.
* !weather - current weather conditions for a specified location.
* !forecast - 5 day weather forecast for a specified location.
* !poll - Start a question with options users can vote on.
* !roles - Display a list of roles users can add to their accounts.
* !urban - Search for an Urban Dictionary definition.
* !report - Anonymously report user to society committee.
* !hangman - Play an interactive game of Hangman.
* !define - Get a dictionary definition of a specified word.
  
## Changelog
* 0.5 - in development.
  * !define - Get a dictionary definition of a specified word.
* 0.4
  * !xckd - Get a random XCKD comic.
  * !eightball - Get some classic 8-ball wisdom.
  * !wiki - Get the first few sentences of a Wikipedia page.
  * !roles - Revamp roles command to be more intuitive.
  * !hangman - Play an interactive game of Hangman.
* 0.3
  * !roles - Users can add non-functional roles to their own accounts, e.g. "2nd Year" or "Graduate".
  * !urban - Search for an Urban Dictionary definition.
  * !report - Anonymously report user to society committee.
* 0.2
  * !random - Random number generator.
  * !dice - Roll a 6 sided dice.
  * !math - some basic math functions.
  * !quote - quote a random message from a user in the channel.
  * Palpatine "power" meme.
  * !weather - current weather conditions for a specified location.
  * !forecast - 5 day weather forecast for a specified location.
  * !poll - Start a question with options users can vote on.
* 0.1
  * Automatic new member welcome message.
  * !say - Make Bjarne repeat a message.
  * !bjarnequote - Display a quote from Bjarne Stroupstrup, creator of C++.
