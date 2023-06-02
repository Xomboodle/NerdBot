"""main.py"""

# Imports
import os

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

import random

import meme_get

import json

import asyncio

from webserver import keep_alive

from dotenv import load_dotenv

# Constants
TOKEN = os.environ.get('BOT_SECRET')
CRATE_IMAGE = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTPfxjHhIv" \
              "-xFHAsZNnLmjPyba-AgbcE0jwNcN-B7LR8EPMWnGObIkQEGTSmlWXMrXe0Pc&us" \
              "qp=CAU"
CLAM_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Clams_" \
             "on_Sandy_Hook_beaches_-_panoramio.jpg/800px-Clams_on_Sandy_Hook_" \
             "beaches_-_panoramio.jpg"
REACTION_IMAGES = {
    "💩": 'https://tenor.com/view/elmo-poop-gif-18814641',
    "👍": 'https://tenor.com/view/boy-kid-computer-thumbs-up-face-gif-9548945',
    "sip": 'https://tenor.com/view/espresso-classy-pinkies-up-sips-tea-sipping'
           '-gif-7250101',
    "beans": 'https://tenor.com/view/dance-bean-dancing-cute-funny-gif-'
             '21992996',
    "hmm": 'https://tenor.com/view/hmm-dot-dot-dot-stick-figure-intresting-gif'
           '-23376515',
    "surprisePog": 'https://tenor.com/view/pog-frog-frog-pog-frog-dance-gif-'
                   '20735320',
    "sus": 'https://tenor.com/view/hmm-suspect-gif-22611582'
}
RARITY_NAMES = ["Uncommon", "Rare", "Epic", "Legendary"]
MONSTER_RARITY = [500, 250, 50, 5]  # Randomiser is 0-1000
BASE_ITEM_RARITY = [5000, 2500, 1000, 100, 1]  # Randomiser is 0-10000
ITEM_RARITY_MODIFIERS = [[200, 100, 0, 0, 0],
                         [500, 200, 50, 0, 0],
                         [1000, 400, 70, 5, 0],
                         [2500, 1000, 200, 100, 1]]
# Constant for rpg commands rules
RPG_HELP_EMBED = discord.Embed(
    title="RPG Help (Prefix !)",
    color=discord.Color.dark_red()
)
RPG_HELP_EMBED.add_field(
    name="start",
    value="```Create your character.```"
)
RPG_HELP_EMBED.add_field(
    name="end",
    value="```Delete your character. This will permanently erase your"
          " character's data.```"
)
RPG_HELP_EMBED.add_field(
    name="profile",
    value="```View your character's profile.```"
)
RPG_HELP_EMBED.add_field(
    name="battle <level[1-6]>",
    value="```Fight a number of monsters to gain exp and items.\n"
          "Recommended player levels for each monster level:\n"
          "Level 1: Player 1-5\nLevel 2: Player 6-10\nLevel 3: Player 11-15\n"
          "Level 4: Player 16-20\nLevel 5: Player 20-25\nLevel 6: Player 26+"
          "```"
)

# Global Variables
# guild = None
crate_embed = None
clam_embed = None
last_react = None


# Set variables in a .env file as environment variables
load_dotenv()

"""
    Setting up the bot. This includes permissions, the activity displayed
    on the profile, and the bot itself.
"""
# Permissions
intents = discord.Intents.all()
# Bot activity
activity = discord.Activity(type=discord.ActivityType.listening,
                            name="cries of anguish")
# Creating the bot
bot = commands.Bot(command_prefix='!', activity=activity,
                   help_command=None, intents=intents)

# Section One: Automatic processes


@bot.listen()
async def on_ready():
    """Runs on startup.
    If an update has happened since the last refresh of the bot, it will be
    displayed in the default channel of the server it runs on.
    """
    # Global variables
    # global guild

    # Sets guild i.e. the server the bot is on
    # guild = bot.get_guild(int(os.environ.get('SERVER_ID')))

    # Reads changelog file
    with open('changelog.txt', 'r') as r_file:
        lines = r_file.read().split('\n\n')
    # Checks if update has been added, applies Discord markdown
    recent_update = lines[0] + "```"
    with open('updated.txt', 'r') as r_file:
        update_lines = r_file.read()
    if recent_update != update_lines:
        with open('updated.txt', 'w') as w_file:
            w_file.write(recent_update)
        for guild in bot.guilds:
            channel = guild.system_channel
            await channel.send(f"NEW UPDATE:\n{recent_update}")


@bot.listen()
async def on_message(message):
    """Listens for messages.
    The bot responds to keywords in user messages (this is different to
    commands called by the user). The bot also has a chance to spawn a crate
    or a clam, which users can collect with the `claim` command.
    """
    # Globals
    global crate_embed
    global clam_embed

    message_content = message.content
    # Checks that the message sent was not by the bot itself.
    if message.author == bot.user:
        return
    # Randomises chance of crate or clam spawning.
    num = random.randint(1, 50)
    if num == 1:
        crate_embed = [discord.Embed(
            title="A wild loot crate appeared!",
            color=discord.Color.green()
        ), None]
        crate_embed[0].set_image(url=CRATE_IMAGE)
        crate_embed[0].add_field(
            name="Grab it quick!",
            value="Type `!claim` to collect the crate.",
            inline=False
        )
        crate_embed[1] = await message.channel.send(embed=crate_embed[0])
    elif num == 2:
        clam_embed = discord.Embed(
            title="A wild clam appeared!",
            color=discord.Color.blue()
        )
        clam_embed.set_image(url=CLAM_IMAGE)
        clam_embed.add_field(
            name="Legit or quit.",
            value="Type `!clam` to claim the clam.",
            inline=False
        )
        await message.channel.send(embed=clam_embed)

    # Checks for keywords
    if "work" in message_content:
        await message.channel.send(
            "Did you just say 'WORK'?! You should be gaming!"
        )
    elif bot.command_prefix == message_content:
        await message.channel.send("Huh? Whaddya want?")


@bot.listen()
async def on_reaction_add(reaction, user):
    """Listens for user reactions.
    The bot will respond with its own reaction to certain reactions made by
    users. To prevent abuse of this feature by spamming a reaction, the last
    user that the bot responded to is recorded, so they cannot force the bot
    to send loads of messages.
    """
    # Globals
    global last_react
    # Checks current user
    if user == last_react:
        return
    else:
        last_react = user
    try:
        reaction_name = str(reaction.emoji.name)
    except AttributeError:
        reaction_name = reaction.emoji
    # Sends corresponding message based on reaction made.
    if reaction_name in REACTION_IMAGES:
        await reaction.message.channel.send(REACTION_IMAGES[reaction_name])


# Section 2: Functions.


def update_score(name: str, difference: int):
    """Updates a user's score on the leaderboard.
    This is used in conjunction with the 'gambling' commands.
    """
    # Load the leaderboard file.
    with open('leaderboard.json', 'r') as r_file:
        leaderboard = json.load(r_file)
    if name in leaderboard:
        updated_score = leaderboard[name] + difference
    else:
        leaderboard[name] = difference
        updated_score = 10
    # The user's score will never go below 1, to prevent them from not being
    # able to use the gambling commands.
    if updated_score < 1:
        updated_score = 1
    leaderboard[name] = updated_score
    with open('leaderboard.json', 'w') as w_file:
        json.dump(leaderboard, w_file)


# Section 3: User Commands


@bot.command()
@has_permissions(manage_permissions=True)
async def bonk(ctx, member: discord.Member):
    """Restricts user messages.
    The user's permissions to send messages across the server are revoked.
    """
    # Validate inputs
    if not isinstance(member, discord.Member):
        await ctx.send(f"{member} is an invalid input.")
        return
    # Restrict user
    for channel in ctx.guild.text_channels:
        permissions = channel.overwrites_for(member)
        permissions.send_messages = False
        await channel.set_permissions(
            member,
            overwrite=permissions,
            reason="Bonk!")
    await ctx.send(f"<@!{member.id} has been sent to jail.")


@bot.command()
@has_permissions(manage_permissions=True)
async def unbonk(ctx, member: discord.Member):
    """Unrestricts user messages.
    The user's permissions to send messages across the server are restored.
    """
    # Validate inputs
    if not isinstance(member, discord.Member):
        await ctx.send(f"{member}> is an invalid input.")
        return
    # Unrestrict user
    for channel in ctx.guild.text_channels:
        permissions = channel.overwrites_for(member)
        permissions.send_messages = True
        await channel.set_permissions(
            member,
            overwrite=permissions,
            reason="Unbonk!"
        )
    await ctx.send(f"<@!{member.id}> has been released from jail.")


@bot.command()
async def recent(ctx):
    """Display the most recent update to the bot."""
    with open('updated.txt', 'r') as r_file:
        lines = r_file.read()
    await ctx.channel.send(lines)


@bot.command()
async def update(ctx):
    """Display full changelog of the bot."""
    with open('changelog.txt', 'r') as r_file:
        message = r_file.read()
    message = message[:2000]
    count = 1
    end_character1 = message[-count]
    end_character2 = message[-(count+1)]
    while end_character1 != "\n" or end_character2 != "\n":
        count += 1
        end_character1 = message[-count]
        end_character2 = message[-(count+1)]
    message = message[:-count] + "```"
    await ctx.channel.send(message)


@bot.command()
async def insult(ctx, arg=None):
    """Chooses a random joke insult.
    The command user chooses another user to insult. Their message is then
    deleted, to provide anonymity to the insult. If the command user does not
    specify another user, the insult is applied to themselves.
    """
    if arg is None:
        arg = f"<@!{ctx.message.author.id}>"
    # Delete original message for anonymity
    await ctx.message.delete()

    insults = [
        f"Wow, {arg}'s face is looking real ugly today.",
        f"Ew, do you smell that? Oh, that's just {arg}",
        f"We thought they went to Mordor to throw the One Ring in Mount Doom,"
        f"but it was actually to get away from {arg}",
        f"If {arg} was a Pokemon, they would be the only one Ash wouldn't catch",
        f"Reverse insult! {arg} is looking lovely today, whereas you,"
        f" <@!{ctx.message.author.id}>, wish only to spread hate across the world."
        f" Meanie.",
        f"{arg} is proof light travels faster than sound. They appear bright"
        f" until they speak.",
        f"{arg}'s mother is a hamster and their father smells of elderberries!",
    ]

    chosen = random.randint(0, len(insults)-1)
    await ctx.channel.send(insults[chosen])


@bot.command()
async def smite(ctx, arg=None):
    """Smites another user."""
    if arg is None:
        arg = f"<@!{ctx.message.author.id}>"
        await ctx.channel.send(f"{arg} was confused, and hurt themselves!")
        return
    await ctx.channel.send(f"The gods dislike you, {arg}. They smite you into"
                           f" oblivion.")


@bot.command()
async def meme(ctx):
    """Display a meme.
    Utilises an API to fetch a collection of memes from reddit and display one
    at random.
    """
    meme_embed = discord.Embed(title="", description="")

    reddit_memes = meme_get.RedditMemes()
    memes = reddit_memes.get_memes(100)
    meme_embed.set_image(url=memes[random.randint(0, 99)].get_pic_url())

    await ctx.channel.send(embed=meme_embed)


# noinspection PyUnresolvedReferences
@bot.command()
async def claim(ctx):
    """Claim a crate.
    If a crate has spawned, and is unclaimed, a user can claim it for bonus
    coins. This only applies to the most recent spawned crate, any prior will
    not count as unclaimed.
    """
    # Globals
    global crate_embed

    if crate_embed is None:
        return
    user = ctx.guild.get_member(ctx.author.id)
    score = random.randint(10, 30)

    await ctx.channel.send(
        f"{user.name if user.nick is None else user.nick} claimed the crate. They got {score} coins!"
    )

    update_score(str(user.id), score)

    # Prepare edited message to replace the original crate spawn
    edited_embed = discord.Embed(
        title="Crate claimed!",
        color=discord.Color.green()
    )
    edited_embed.add_field(
        name="",
        value=f"{user.name if user.nick is None else user.nick} claimed this crate."
    )
    await crate_embed[1].edit(embed=edited_embed)
    crate_embed = None


@bot.command()
async def clam(ctx):
    """Claim a clam.
    Functions the same as the 'claim' command, but for clam spawns instead.
    """
    # Globals
    global clam_embed

    if clam_embed is None:
        await ctx.channel.send("No clam to claim.")
        return
    clam_embed = None
    await ctx.channel.send(
        f"{ctx.author.name if ctx.author.nick is None else ctx.author.nick} claimed the clam. Claiming the clam clears"
        f" the clog of clams to claim, 'til another clam comes along."
    )


# noinspection PyUnresolvedReferences
@bot.command()
async def highscore(ctx):
    """Display the leaderboard.
    Returns an embed detailing the ranking of users based on the number of
    coins they have.
    """

    with open('leaderboard.json', 'r') as r_file:
        leaderboard = json.load(r_file)
    # Sort the leaderboard based on score
    leaderboard = dict(
        sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)
    )
    # Create Embed for the leaderboard
    leaderboard_users = [*leaderboard]
    leaderboard_values = [*leaderboard.values()]
    leaderboard_embed = discord.Embed(
        title="Gambling Leaderboard",
        color=discord.Color.red()
    )
    # Add fields for the top 10 users
    position = 0
    skipped = 0
    while position < 10:
        try:
            user = ctx.guild.get_member(int(leaderboard_users[position+skipped]))
            if user is None:
                skipped += 1
                continue
        except IndexError:
            # In event of less than 10 users in JSON file
            break

        if user.nick is not None:
            leaderboard_embed.add_field(
                name=f"{position+1} {user.nick}",
                value=f"{leaderboard_values[position]} coins",
                inline=False
            )
        else:
            leaderboard_embed.add_field(
                name=f"{position + 1} {user.name}",
                value=f"{leaderboard_values[position]} coins",
                inline=False
            )
        position += 1

    await ctx.channel.send(embed=leaderboard_embed)

    with open('leaderboard.json', 'w') as w_file:
        json.dump(leaderboard, w_file)


@bot.command()
async def coins(ctx):
    """Display how many coins an individual user has."""

    with open('leaderboard.json', 'r') as r_file:
        leaderboard = json.load(r_file)
    # Check if user has gambled before. If not, assign default 10 coins.
    if str(ctx.author.id) not in leaderboard:
        update_score(str(ctx.author.id), 10)
        await ctx.channel.send("You have 10 coins.")
    else:
        await ctx.channel.send(f"You have {leaderboard[str(ctx.author.id)]} coins.")


@bot.command()
async def rps(ctx, arg=None, arg2=0):
    """Play a game of rock, paper, scissors.
    The user can choose which option to choose, and how much to gamble. They
    cannot gamble more coins than they have available.
    """

    choices = ["rock", "paper", "scissors"]
    with open('leaderboard.json', 'r') as r_file:
        leaderboard = json.load(r_file)
    user = str(ctx.author.id)
    if user not in leaderboard:
        update_score(user, 10)

    # Validate choice and coin amount
    if arg is None or arg.lower() not in choices:
        await ctx.channel.send("Invalid choice.")
        return
    if arg2 < 0 or arg2 > leaderboard[user]:
        await ctx.channel.send("You can't bet that!")
        return
    # Allow for float inputs, but change to integers
    arg2 = arg2 // 1
    player_choice = choices.index(arg.lower())
    bot_choice = random.randint(0, 2)

    if bot_choice == player_choice:
        # Tie results
        await ctx.channel.send("It was a tie!")
    elif (bot_choice - player_choice == 1) \
            or (bot_choice - player_choice == -2):
        # Loss results
        await ctx.channel.send(
            f"I chose {choices[bot_choice]}. You lose {arg2} coins."
        )
        update_score(user, -arg2)
    else:
        # Win results
        await ctx.channel.send(
            f"I chose {choices[bot_choice]}. You win {arg2} coins!"
        )
        update_score(user, arg2)


@bot.command()
async def start(ctx):
    """Create a new character.
    Users can make a character for the RPG commands. If they already have a
    character, they cannot make another.
    """

    def check(message):
        if message.author == ctx.author and message.channel == ctx.channel:
            return True
        return False

    # Confirm character does not already exist
    user = str(ctx.author.id)
    with open('rpg.json', 'r') as r_file:
        rpg = json.load(r_file)
    if user in rpg["players"]:
        await ctx.channel.send("You already have a character.")
        return
    await ctx.channel.send("What is your character's name?")

    # Exception on user taking too long to respond
    try:
        response = await bot.wait_for("message", check=check, timeout=30)
    except asyncio.TimeoutError:
        await ctx.channel.send("You did not respond in time, command aborted.")
        return

    # Set up character
    rpg["players"][user] = {}
    rpg["players"][user]["name"] = response.content
    rpg["players"][user]["level"] = 1
    rpg["players"][user]["health"] = 10
    rpg["players"][user]["strength"] = 1
    rpg["players"][user]["exp"] = 0
    rpg["players"][user]["items"] = {}

    with open('rpg.json', 'w') as w_file:
        json.dump(rpg, w_file)

    await ctx.channel.send("Character created.")


@bot.command()
async def profile(ctx):
    """Displays the character profile for a user.
    If the user does not have a character, the bot responds accordingly.
    """

    user = str(ctx.author.id)
    with open('rpg.json', 'r') as r_file:
        rpg = json.load(r_file)

    # Check character exists
    if user not in rpg["players"]:
        await ctx.channel.send(
            "You don't have a character! Use `!start` to make one."
        )

    # Create profile Embed
    profile_embed = discord.Embed(
        title=rpg["players"][user]["name"],
        description=f"<@!{ctx.author.id}>'s character"
    )
    profile_embed.set_thumbnail(url=ctx.author.avatar_url)
    profile_embed.add_field(
        name="Level:",
        value=f"```{rpg['players'][user]['level']}```"
    )
    profile_embed.add_field(
        name="EXP:",
        value=f"```{rpg['players'][user]['exp']}```"
    )
    profile_embed.add_field(
        name="Health:",
        value=f"```{rpg['players'][user]['health']}```"
    )
    profile_embed.add_field(
        name="Strength:",
        value=f"```{rpg['players'][user]['strength']}```"
    )
    for i in range(2):
        profile_embed.add_field(
            name="\u200b",
            value="\u200b"
        )
    
    # Create list of items the character has
    item_names = [*rpg["players"][user]["items"]]
    item_values = [*rpg["players"][user]["items"].values()]
    items = ""
    for count, item in enumerate(item_names):
        items += f"{item} x {item_values[count]}\n"

    profile_embed.add_field(
        name="Items:",
        value=f"```\n{items}```",
        inline=False
    )

    await ctx.channel.send(embed=profile_embed)


@bot.command()
async def end(ctx):
    """Removes user's character.
    A confirmation is first sent to make sure the user wants to delete their
    character. If yes, all data related to their character is removed.
    """

    def check(message):
        if message.author == ctx.author and message.channel == ctx.channel:
            return True
        return False

    with open('rpg.json', 'r') as r_file:
        rpg = json.load(r_file)

    if str(ctx.author.id) not in rpg["players"]:
        await ctx.channel.send(
            "You don't have a character yet, so you can't delete one."
        )
        return

    await ctx.channel.send("Are you sure you want to delete your character?"
                           "Type 'Y/y' for yes, or anything else for no.")
    try:
        response = await bot.wait_for("message", check=check, timeout=30)
    except asyncio.TimeoutError:
        await ctx.channel.send("You did not respond in time, command aborted.")
        return

    if response.content.lower() != "y":
        await ctx.channel.send("Command aborted.")
        return

    # Remove character from JSON file
    del rpg["players"][str(ctx.author.id)]

    with open('rpg.json', 'w') as w_file:
        json.dump(rpg, w_file)

    await ctx.channel.send("Character deleted.")


@bot.command()
async def battle(ctx, level=None):
    """Uses user's character to battle monsters.
    The character gains experience points if their fight is a success. The
    user specifies the level of monster that they want to fight."""

    user = str(ctx.author.id)

    if level is None:
        await ctx.channel.send("No level selected.")
        return

    try:
        level = int(level)
    except ValueError:
        await ctx.channel.send("Invalid level.")
        return

    with open('rpg.json', 'r') as r_file:
        rpg = json.load(r_file)

    # Check user has character
    if user not in rpg["players"]:
        await ctx.channel.send("You don't have character! Type `!start` to"
                               " make one.")
        return

    # Get list of monsters with specified level
    use_monsters = []
    for monster in rpg["monsters"].keys():
        print(monster)
        # Excepting LV 6, all monsters of equal or lower level can be fought.
        # For LV 6, only LV 6 monsters can be fought.
        if rpg["monsters"][monster]["level"] <= level != 6:
            temp_dict = {monster: rpg["monsters"][monster]}
            use_monsters.append(temp_dict)
        elif rpg["monsters"][monster]["level"] == level == 6:
            temp_dict = {monster: rpg["monsters"][monster]}
            use_monsters.append(temp_dict)

    # Determine arbitrary number of monsters to fight
    if level == 6:
        total_monsters = 1
    else:
        total_monsters = random.randint(2+random.randint(0, level),
                                        10+random.randint(0, level))

    # Determine monsters to actually fight
    to_fight = {}
    total_strength = 0
    item_rarities = BASE_ITEM_RARITY.copy()
    for add in range(total_monsters):
        to_add_number = random.randint(0, len(use_monsters)-1)
        to_add_monster = [*use_monsters[to_add_number].values()]
        # Determine rarity of monster
        rare_value = random.randint(0, 1000)
        for value in range(len(MONSTER_RARITY)-1, -1, -1):
            if (1000 - rare_value) <= value:
                rarity_name = f"[{RARITY_NAMES[MONSTER_RARITY.index(value)]}]"
                rarity_multiplier = 2 + MONSTER_RARITY.index(value)
                break
        else:
            rarity_name = ""
            rarity_multiplier = 1
        # Determine changes to item spawn rarity
        if rarity_name != "":
            modifiers = ITEM_RARITY_MODIFIERS[RARITY_NAMES.index(rarity_name[1:-1])]
            for count in range(len(item_rarities)):
                item_rarities[count] += modifiers[count]
            for value in range(len(item_rarities)):
                if item_rarities[value] > 10000:
                    item_rarities[value] = 10000

        total_strength += (to_add_monster[0]["strength"] * rarity_multiplier)

        name = f"{list(use_monsters[to_add_number].keys())[0]} {rarity_name}"
        if name in to_fight:
            to_fight[name]["count"] += 1
        else:
            to_fight[name] = {}
            to_fight[name]["count"] = 1

    # Determine outcome of battle
    contested_value = total_strength + random.randint(0, 1+(level*(level-1)))
    if (rpg["players"][user]["health"] / (total_strength / total_monsters))\
            - (total_monsters - 1) < \
            (contested_value / rpg["players"][user]["strength"]):
        win = False
    else:
        win = True

    # Generate result of battle
    if win:
        result_color = discord.Color.green()
    else:
        result_color = discord.Color.red()
    results_embed = discord.Embed(
        title="Battle Results",
        color=result_color
    )
    results_embed.add_field(
        name=f"You {'won!' if win else 'lost!'}",
        value="\u200b"
    )
    fought_text = ""
    for fought in to_fight:
        fought_text += f"{fought} x {to_fight[fought]['count']}\n"
    results_embed.add_field(
        name="Monsters fought:",
        value=f"```\n{fought_text}```",
        inline=False
    )
    if win:
        rpg["players"][user]["exp"] += contested_value - level
        results_embed.add_field(
            name="EXP Gained:",
            value=f"{contested_value - level}",
            inline=False
        )
        # If exp reaches level up threshold
        if rpg["players"][user]["exp"] >=\
                ((rpg["players"][user]["level"] * 20)
                 + ((rpg["players"][user]["level"] ** 3) - 1)):
            rpg["players"][user]["level"] += 1
            rpg["players"][user]["exp"] = 0
            rpg["players"][user]["health"] += 5
            rpg["players"][user]["strength"] += 1
            results_embed.add_field(
                name="Level Up!",
                value=f"Level increased to {rpg['players'][user]['level']}. "
                      f"All stats boosted."
            )
        # Determine if item acquired
        item_chance = random.randint(1, 10000)
        for value in range(len(item_rarities)-1, -1, -1):
            if (10000 - item_chance) < value:
                # TODO:
                #  Give item to player
                break

    with open('rpg.json', 'w') as w_file:
        json.dump(rpg, w_file)

    await ctx.channel.send(embed=results_embed)


@bot.command()
async def helprpg(ctx):
    """Display possible commands the user can perform, related to the RPG
    elements."""
    await ctx.channel.send(embed=RPG_HELP_EMBED)


@bot.command()
async def help(ctx):
    """Display possible commands the user can perform.
    An Embed is used to display all the possible commands.
    """
    help_embed = discord.Embed(
        title="Command Help (Prefix !)",
        color=discord.Color.blurple()
    )
    help_embed.add_field(
        name="bonk <user>",
        value="```Send a user to jail. Requires Manages Permissions to use."
              "```"
    )
    help_embed.add_field(
        name="claim",
        value="```Claim a crate if there is one available.```"
    )
    help_embed.add_field(
        name="clam",
        value="```Claim a clam if there's a clam to claim. This has no benefit"
              " towards the leaderboard.```"
    )
    help_embed.add_field(
        name="coins",
        value="```See how many coins you have, and weep in despair when they"
              "are all gone.```"
    )
    help_embed.add_field(
        name="help",
        value="```It's what you're doing now.```"
    )
    help_embed.add_field(
        name="highscore",
        value="```See who's better, or worse, at gambling their life "
              "savings.```"
    )
    help_embed.add_field(
        name="insult <user>",
        value="```Will violently attack the mentioned user (not really).```"
    )
    help_embed.add_field(
        name="meme",
        value="```Displays a meme from r/memes.```"
    )
    help_embed.add_field(
        name="recent",
        value="```Check the most recent update the bot has, in case you missed"
              " it.```"
    )
    help_embed.add_field(
        name="helprpg",
        value="```View commands related to adventuring.```"
    )
    help_embed.add_field(
        name="rps <option[rock,paper,scissors]> <bet>",
        value="```A simple game of rock, paper, scissors.```"
    )
    help_embed.add_field(
        name="smite <user>",
        value="```Summon the power of the gods on some poor unfortunate soul.```"
    )
    help_embed.add_field(
        name="unbonk <user>",
        value="```Release a user from jail. Requires Manages Permissions.```"
    )
    help_embed.add_field(
        name="update",
        value="```See a bunch of more recent updates in one long, horrible list.```"
    )
    await ctx.channel.send(embed=help_embed)


# Run the bot
try:
    keep_alive()
    bot.run(TOKEN)
except discord.errors.HTTPException:
    os.system('kill 1')
    os.system('python restarter.py')
