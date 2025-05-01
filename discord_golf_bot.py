import discord
from discgolf_course_query import query
import asyncio
import re

TOKEN = "MTM2MTc5MTA2MjEzMzMwOTY3Mg.GR6m5t.SDE3InuirLmax21nywmSH-qLRHRvjpSd3PVevo"

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)



@client.event
async def on_ready():
    print(f'{client.user} is connected to the following server:\n')
    for server in client.guilds:
        print(f'{server.name}(id: {server.id})')

kept_answer_object = None
kept_scores_list = []

@client.event
async def on_message(message):
    global kept_answer_object
    global kept_scores_list
    if message.author == client.user:
        return
    if message.content.startswith('!find'):
        match = re.search(r"^!find\s+(.*?)\s*$", message.content)
        if match:
            search_term = match.group(1)
            # call scraper
            answer_object = await query(search_term)
            kept_answer_object = answer_object
            #
            answer_text = f"At {answer_object.site}, the holes are:\n"
            for hole in answer_object.holes_list:
                answer_text += f"Hole {hole.hole} Par {hole.par}\n"
            #
            await message.channel.send(answer_text)
        else:
            await message.channel.send(f'Find what disc golf course?')
    if message.content.startswith('!enter'):
        if not kept_answer_object:
            await message.channel.send(f'First do a !find course name')
        else:
            match = re.search(r"^!enter\s*(\d+)(?:\s*at\s*(\d+))?\s*$", message.content)
            if (match):
                hole_my_score = int(match.group(1))
                if (match.group(2)):
                    hole_number = int(match.group(2))
                else:
                    hole_number = 1 + len(kept_scores_list) # next
                while hole_number - 1 > len(kept_scores_list): # in case skipped one or a few
                    kept_scores_list.append(None) # fill empty spots with None
                if hole_number - 1 == len(kept_scores_list): # if a new entry, most common use
                    kept_scores_list.append(hole_my_score)
                if hole_number - 1 < len(kept_scores_list): # in case overwriting a  previous entry
                    kept_scores_list[hole_number - 1] = hole_my_score
                #
                # show what we have so far
                scores_list_text = f"Your scores ({kept_answer_object.site}) so far:\n"
                i = 0
                for hole in kept_answer_object.holes_list:
                    if (i >= len(kept_scores_list)):
                        break # skip the upcoming holes for this list
                    scores_list_text += f"Hole {hole.hole} Par {hole.par}"
                    if (i < len(kept_scores_list)):
                        scores_list_text += f" Score {kept_scores_list[i]}"
                    scores_list_text += "\n"
                    i = i + 1
                await message.channel.send(scores_list_text)
            else:
                await message.channel.send(f'Use !enter 7 for score, or !enter 7 at 1 for score at hole')
    if message.content.startswith('!show'):
        if not kept_answer_object:
            await message.channel.send(f'First do an !find course name')
        else:
            scores_list_text = f"At {kept_answer_object.site}, your scores are:\n"
            i = 0
            for hole in kept_answer_object.holes_list:
                scores_list_text += f"Hole {hole.hole} Par {hole.par}"
                if (i < len(kept_scores_list)):
                    scores_list_text += f" Score {kept_scores_list[i]}"
                scores_list_text += "\n"
                i = i + 1
            await message.channel.send(scores_list_text)
    if message.content.startswith('!clear'):
        kept_scores_list.clear()
        await message.channel.send(f'Cleared your score')
    if message.content.startswith('!help') or message.content.startswith('!?'):
        await message.channel.send(f'The commands are !find, !enter, !show, !clear, !help')


client.run(TOKEN)
