# ABotmo

A bot for Veemocord™: A fork of Vesktop

| ![image](https://github.com/user-attachments/assets/0255adf2-70c4-489c-add6-0ee6eb93a829) |
| :--------------------------------------------------------------------------------------------------: |
|   A screenshot showing the bot's [server profile](https://discord.com/oauth2/authorize?client_id=1331719784374468678&integration_type=0&scope=applications.commands)    |

## Features

The bot includes:
- 8 moderation commands
- 14 miscellanous commands
- 9 fun commands
- Saving user roles and reapplying to them on rejoin
- Databases
- Moderation logging
- Bot Status detection
- Channel-topic updating
- Logging all commands in console
- Filtering words and spam
- Permission checking
- & more, soon...

## Key Info

The bot's commands are not suited for other guilds, so as of now (27/03/2025 DD/MM) moderation commands and other(s) are disabled. I do not see any one using the bot in their server so unless someone wants to I will then make a database for more servers and enable all commands.

You will not get all commands for ABotmo in DMs as I have not been verified, and in the Server you will need to install it into your account to see the rest of the commands. However for the server command issue, it'll be removed after the above issue is resolved.

## Goals
(07/04/2025)

| ![image](https://github.com/user-attachments/assets/84e88388-fb10-4fde-b15b-5224df83ebd0) |
| :--------------------------------------------------------------------------------------------------: |
| Screenshot providing info for Goals: Open source & Databases for multiple guilds. (1 SERVER IS EXCLUDED) |

- Open Source: 100 User Installs

- Databases for multiple guilds: 5+ Server invites requested

## LATEST UPDATE - V6.3d | PARTY STARTER
[Discord Message Link](https://discord.com/channels/680125280412762115/1331742971858518066/1357871092949323776)


## 「 __TL;DR__ 」
- 5 new commands!
- UX Updates!
- New command category module!
- QoL improvements (me)

## 「 __Bug Fixes__ 」
- Fixed /yukerlist saying "too big of a number" (or whatever) when it wasnt
- Fixed all guild commands not working
- Fixed all global commands "working" (they didnt send any interaction responses)
- Fixed Bot Status message not sending
- Fixed text on /applications embed

*Not many bug fixes since I patched them all last update 🤑*

## 「 __Changes__ 」
- Overhauled /help menu to be categories
- Changed /yukerlist to specify errors (all errors had the same error message)
- Changed /agecheck code to take more user data and determine "better"
- Made the code more cleaner and made it organized
- Removed tons of checks and unnecessary code
- Removed user data that was no longer needed
- Removed functions & libraries that was not being used

## 「 __Additions__ 」
- Added except statements in most commands to catch more errors
- Added more "fun" message triggers
- Added activity status cycling for the bot
- Added 5 new commands that i spent way too long on please help me im suffering why me

# 4 NEW GUILD COMMANDS!
___**NEW COMMAND CATEGORY:**___

「 **__MUSIC__** 」


🔷 /play
- Enter a search query, string/text or a link the bot will find whatever!

If you enter string/text, the bot will find the first video on YouTube!

If you enter a link, make sure its only a youtu.be.com or a youtube.com link as the bot only supports those!

- The queue system is a bit buggy, so when putting a new song into the queue it may bug out and lag out the music player

- Music player is currently experimental! And you all get "early access", issues I've encountered so far:

1. "Music stopping randomly"

🔷 /skip
- Skip the current song and play the next song in queue

If no songs in queue left it will leave automatically

🔷 /stopm
- Clear the music queue and make the bot leave the voice channel

🔷 /musicqueue
- Display the music queue!

Sorry for the long name, variables is an ass

**ALL COMMANDS IN MUSIC CATEGORY ARE CURRENTLY EXPERIMENTAL, EXCEPT LOW QUALITY AND BUGS/ERRORS!**

# 1 NEW GLOBAL COMMAND!
🔷 /optout
- Use this to opt out of PUBLIC command logs only!
- Due to this bot being experimental and not being fully out we have public and private command logs, and if you'd like to opt out of command logs you can use this command

There will be a waiting list since im too lazy to make a database and im using a list so i will need to manually update the list
