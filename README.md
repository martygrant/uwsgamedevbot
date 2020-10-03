# Bjarne

Bjarne is a Discord server bot built for and maintained by the UWS Game Dev Society.

It is written in Python using [discord.py](https://github.com/Rapptz/discord.py), a wrapper for the Discord API.

It is currently hosted on the Heroku cloud platform.

### Requirements
* Python 3.4.2+
* [discord.py](https://github.com/Rapptz/discord.py)
* [requests](https://pypi.org/project/requests/)
* [wikipedia](https://github.com/goldsmith/Wikipedia)

### Contributors
* [Medallyon](https://github.medallyon.me/)

## Contributing
If you are a member of the society and wish to add features, enhancements, or fix bugs, your contribution is welcome!

Feel free to choose an item on the [Issues page](https://github.com/martygrant/uwsgamedevbot/issues) section that you would like to work on. Already implemented features are [listed below](#features).

To get started you should get the example running from the [discord.py repo](https://github.com/Rapptz/discord.py) and check out the documentation there. For a more in-depth tutorial there is a really handy [Discord server](https://discord.gg/GWdhBSp) with guides for basic operations.

For developing the bot you should create your own bot and run it in your own private server to test out your functions so we can avoid a lot of bother with security tokens and the Bjarne bot being hosted in a cloud server. Once you are happy you can submit a pull request and it can be added to Bjarne.

If you have any questions for making a contribution, or a code related question, feel free to send a message in the `#bjarne-dev` channel on the society server.

## Installation

[Fork this repo](https://github.com/martygrant/uwsgamedevbot/fork) and clone your fork to get it onto your computer. Make sure you have [`git`](https://git-scm.com/) installed before you do this.

```bash
git clone https://github.com/<YOUR_GITHUB_USERNAME>/uwsgamedevbot.git
```

Install any dependencies you may need:

```bash
pip install -r requirements.txt
```

Set up your environment:

1. Create a new file in the root of the repo directory called `.env`
    1. If you struggle doing this on Windows, you can just open a text editor window and do `Save As...`, then save it into the root of your project folder.
1. Paste the following text into that file, then save it:

```bash
VERSION=0.5

# Replace this with your development bot token from https://discord.com/developers/applications
BOT_TOKEN=

GIPHY_TOKEN=DJMTKL6KeslYSHAY0S0ts7psxsUixP0S
WOLFRAM_TOKEN=42XXHU-YEK7852REU
```
*Some 3rd-Party tokens have been provided for the sake of ease. They are working, but please don't abuse them. In production, different tokens will be used.*

1. (Recommended) Create a development server on Discord for local testing purposes.
1. Create a developer application on the [Discord Applications](https://discord.com/developers/applications) page.
1. Convert it into a `BOT` by clicking the very obvious button that appears on the following page.
1. Navigate to the **OAuth2** tab on the left sidebar
    1. Scroll down and check the `bot` entry in the **SCOPES** section.
    1. Follow the link that is generated in the text field below and invite the bot into the server you created in step 1.
    1. The bot will appear as offline, which is fine, since we haven't started the application yet!
1. Navigate to the **Bot** tab on the left sidebar.
    1. Copy the `Bot Token` and paste it into the `BOT_TOKEN` entry from the `.env` file you created earlier.
1. Now you can run `python main.py` and the bot should be up and running. Feel free to make any changes to the code and restart the bot to see the effects. Once you are satisfied with your changes, push it to your fork, and create a pull request!
    1. **NOTE: As of the time of this writing, the bot may be completely broken and may simply spew errors. This is most likely a dependency issue and is being looked into. If you feel adventurous, please have a look and see if you can get it up and running yourself. That would be a huge help!**

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
* !translate - Translate a message between specified languages.
* !crypto - Get cryptocurrency prices.
  
## Changelog
* 0.5 - in development.
  * !define - Get a dictionary definition of a specified word.
  * !translate - Translate a message between specified languages.
  * !crypto - Get cryptocurrency prices.
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
