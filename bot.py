import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
import random

import sqlite3

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

db =  sqlite3.connect('storyBot.db')
cursor = db.cursor()


cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_stories (
        user_id INTEGER PRIMARY KEY,
        location TEXT,
        item TEXT,
        event TEXT
    )
""")

db.commit()

story_locations = [
    "an abandoned library",
    "a mysterious island",
    "a futuristic city",
    "a hidden underground laboratory",
    "a forest that never appears on maps"
]

story_items = [
    "a glowing key",
    "an ancient notebook",
    "a strange compass",
    "a locked metal box",
    "a mysterious photograph"
]

story_events = [
    "You hear footsteps behind you.",
    "The lights suddenly turn off.",
    "A hidden door opens nearby.",
    "Your phone starts displaying a message from an unknown sender.",
    "You notice that the room has changed."
]

chat_responses = {
    "hello": [
        "Hey! What's up?",
        "Hello! How's your day going?",
        "Hi! What are you working on?"
    ],
    "python": [
        "Python is a great language for beginners because its syntax is pretty readable.",
        "If you're learning Python, try building something instead of only watching tutorials."
    ],
    "discord": [
        "Discord bots are a fun way to practice Python because you get instant feedback.",
        "Once you understand commands and events, you can build some surprisingly complex bots."
    ]
}

support_responses = {
    "stress": [
        "That sounds like a lot to handle. Try breaking the situation into one small task at a time.",
        "When everything feels overwhelming, it can help to pause and focus on what needs attention right now."
    ],

    "school": [
        "School can pile up quickly. Consider choosing one assignment to work on first instead of trying to solve everything at once.",
        "If school stress is getting difficult to manage, talking with a trusted person can make things feel less like something you have to handle alone."
    ],

    "sad": [
        "I'm sorry you're having a difficult moment. Taking a short break, doing something calming, or talking with someone you trust may help.",
        "You don't have to solve everything immediately. Give yourself some time and consider reaching out to someone you trust."
    ]
}

intents = discord.Intents.default()
intents.message_content = True

user_stories = {}

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command()
async def hello(ctx):
    await ctx.send("Hello! I'm online.")

@bot.command()
async def story(ctx):
    user_id = ctx.author.id

    location = random.choice(story_locations)
    item = random.choice(story_items)
    event = random.choice(story_events)

    user_stories[user_id] = {
        "location": location,
        "item": item,
        "event": event
    }

    await ctx.send(
        f"You wake up in {location}.\n\n"
        f"Next to you is {item}.\n\n"
        f"{event}\n\n"
        "What do you do?"
    )


@bot.command()
async def choose(ctx, choice: str):
    user_id = ctx.author.id

    if user_id not in user_stories:
        await ctx.send("You don't have an active story. Try `!story` first.")
        return

    choice = choice.lower()

    if choice == "left":
        response = (
            "You head left and discover a room filled with old maps. "
            "One of them has your name written on it."
        )

    elif choice == "right":
        response = (
            "You head right and find a staircase leading toward "
            "a strange blue light."
        )

    else:
        response = "Try choosing `left` or `right`."

    await ctx.send(response)


@bot.command()
async def chat(ctx, *, message: str):
    text = message.lower()

    for keyword, responses in chat_responses.items():
        if keyword in text:
            await ctx.send(random.choice(responses))
            return

    await ctx.send(
        "I'm still learning how to respond to that. "
        "Try talking to me about Python or Discord!"
    )

@bot.command()
async def support(ctx, *, message: str):
    text = message.lower()

    for keyword, responses in support_responses.items():
        if keyword in text:
            response = random.choice(responses)

            await ctx.send(
                f"{response}\n\n"
                "I'm a bot, not a therapist or medical professional. "
                "If you need personal support, consider talking with "
                "someone you trust."
            )
            return

    await ctx.send(
        "It sounds like something is bothering you. "
        "I can offer general wellness suggestions, but I'm not a therapist. "
        "If you need personal support, consider reaching out to someone you trust."
    )


@bot.command()
async def commands_help(ctx):
    await ctx.send(
        "**Available commands:**\n"
        "`!hello` - Say hello\n"
        "`!story` - Start a new story\n"
        "`!choose left` - Choose the left path\n"
        "`!choose right` - Choose the right path\n"
        "`!chat <message>` - Have a casual conversation\n"
        "`!support <message>` - Get general wellness support"
    )

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "You're missing something. Try `!help` to see how the command works."
        )

    elif isinstance(error, commands.CommandNotFound):
        return

    else:
        print(f"Error: {error}")

@bot.command()
async def status(ctx):
    user_id = ctx.author.id

    cursor.execute(
        """
        SELECT location, item, event
        FROM user_stories
        WHERE user_id = ?
        """,
        (user_id,)
    )

    story = cursor.fetchone()

    if story:
        location, item, event = story

        await ctx.send(
            f"You're currently in {location}. "
            f"You have {item}, and you're facing {event}."
        )
    else:
        await ctx.send(
            "You don't have a saved story yet. "
            "Start one with `!story`!"
        )

bot.run(TOKEN)