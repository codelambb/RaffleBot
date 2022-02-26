import keep_alive
import discord
from discord.ext import commands
import os
import random
import asyncio
import json

client = commands.Bot(command_prefix='$', case_insensitive=True)
client.remove_command("help")

@client.event
async def on_ready():
	print("Bot is ready")
	await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"to Hericulum#6785"))

#get_tickets_data function
async def get_ticket_data():
	with open("tickets.json", "r") as f:
		tickets = json.load(f)

	return tickets

#open_tickets function
async def open_tickets(user):
	tickets = await get_ticket_data()

	if(str(user.id) in tickets):
		return

	else:
		tickets[str(user.id)] = 0

	with open("tickets.json", "w") as f:
		json.dump(tickets, f, indent=4)

#add_tickets function
async def add_tickets(user, amount):
	tickets = await get_ticket_data()
	tickets[str(user.id)] += amount

	with open("tickets.json", "w") as f:
		json.dump(tickets, f, indent=4)

#remove_tickets function
async def remove_tickets(user, amount):
	tickets = await get_ticket_data()
	tickets[str(user.id)] -= amount

	with open("tickets.json", "w") as f:
		json.dump(tickets, f, indent=4)

#get_raffle_data function
async def get_raffle_data():
	with open("raffle.json", "r") as f:
		raffle = json.load(f)

	return raffle

#open_raffle function
async def open_raffle(name, prize, channel):
	raffle = await get_raffle_data()

	if name in raffle:
		return

	else:
		raffle[name] = {}
		raffle[name]["size"] = 0
		raffle[name]["prize"] = prize
		raffle[name]["channel"] = channel

	with open("raffle.json", "w") as f:
		json.dump(raffle, f, indent=4)

#add_raffle function
async def add_raffle(name, user, tickets):
	raffle = await get_raffle_data()
	size = raffle[name]["size"]
	raffle[name][str(user.id)] = {}
	raffle[name][str(user.id)]["range1"] = size + 1
	raffle[name][str(user.id)]["range2"] = (size + 1) + (tickets - 1)
	raffle[name]["size"] += tickets  

	with open("raffle.json", "w") as f:
		json.dump(raffle, f, indent=4)

#remove_raffle function
async def remove_raffle(name):
	raffle = await get_raffle_data()
	del raffle[name]

	with open("raffle.json", "w") as f:
		json.dump(raffle, f, indent=4)

#change_rate function
async def change_rate(rate):
	with open("rate.json", "r") as f:
		tr = json.load(f)

	tr["rate"] = int(rate)

	with open("rate.json", "w") as f:
		json.dump(tr, f, indent=4)

#help command
@client.command()
async def help(ctx):
	em = discord.Embed(title="Help Menu", color=ctx.author.color)
	em.add_field(name="`$tickets (raffle)`", value="Check how many tickets you have in a raffle!", inline=False)
	em.add_field(name="`$list`", value="Check out the raffles going on right now!", inline=False)
	em.add_field(name="`$start (raffle) (prize)`", value="Start a raffle! Command only for Admins", inline=False)
	em.add_field(name="`$end (raffle)`", value="End a raffle and decide a random winner! Command only for Admins", inline=False)
	em.add_field(name="`$rafflehelp`", value="Learn how the raffle giveaway system works!", inline=False)
	em.add_field(name="`$totalTickets (raffle)`", value="See how many the amount of total tickets the raffle has!", inline=False)
	em.add_field(name="`$setRate (rate)`", value="Set the ticket rate! Command only for Admins", inline=False)
	await ctx.send(embed=em)

#setRate command
@client.command()
async def setRate(ctx, rate = None):
	if rate == None:
		await ctx.send("Please enter the rate you want to set for the tickets next time!")
		return

	if ctx.author.id not in [756053421420707928, 796042231538122762, 740883324083503155, 905921030206414898]:
		await ctx.send("You don't have the permissions to use this command!")
		return

	await change_rate(rate)
	await ctx.send(f"Sucessfully changed the rate of the tickets to **{rate}** pkc per ticket!")

#rafflehelp command
@client.command()
async def rafflehelp(ctx):
	em = discord.Embed(tittle="help", description="The raffle system works on tickets and random number generation system.\
	Plesae see the following image below to see how to join a raffle (2 pkc per ticket)!\n\n You can check how many tickets\
	you have currently in a raffle by doing `$tickets (raffle)`.\n\n You can check out current live raffles by doing the `$list` command!\n\n\
	The tickets_use arguement is the range of numbers which you are appointed for example the current number is 5 and you\
	used 700 raffles then your range is 6-705 (including both 6 and 705). When the raffle ends a lucky number is generated\
	if number lies in your range then you win the prize!")
	em.set_image(url="https://media.discordapp.net/attachments/931131516321398794/941936393746251806/unknown.png")
	await ctx.send(embed=em)

#on_message event
@client.event
async def on_message(message):
	msg = message.content

	raffle = await get_raffle_data()
	channels = []

	for i in raffle:
		channels.append(raffle[i]["channel"])

	if ".gift <@!932498512841678938>" in msg and message.channel.id in channels:
		final_msg = msg.replace(".gift <@!932498512841678938>", "")
		final_number = 0
		number = 1

		for word in final_msg.split():
			if word.isdigit():
				final_number += int(word) * number
				number *= 10

		check = True

		while check:				
			if final_number == 1:
				await message.channel.send(f"You got no tickets cause you paid only 1 pkc! The rate is 2 pkc per ticket!")
				return

			elif final_number == 0:
				await message.channel.send(f"You got no tickets cause you paid nothing to us! The rate is 2 pkc per ticket!")
				return

			else:
				await open_tickets(message.author)

				with open("rate.json", "r") as f:
					tr = json.load(f)

				rate = tr["rate"]
				name = None

				for i in raffle:
					if raffle[i]["channel"] == message.channel.id:
						name = i

				previousSize = raffle[name]["size"]		
				await add_raffle(name, message.author, round(final_number / rate))
				raffle = await get_raffle_data()
				currentSize = raffle[name]["size"]
				em = discord.Embed(title="You have sucessfully joined the raffle!", color=message.author.color)
				em.add_field(name="Raffle Name", value=name, inline=False)
				em.add_field(name="User", value=f"<@{message.author.id}>", inline=False)	
				em.add_field(name="Previous Tickets", value=previousSize, inline=True)
				em.add_field(name="Tickets Added", value=round(final_number / rate), inline=True)
				em.add_field(name="Current Tickets", value=currentSize, inline=True)
				await message.channel.send(embed=em)
				return

	await client.process_commands(message)

#tickets command
@client.command()
async def tickets(ctx, name = None, user: discord.Member = None):
	if name == None:
		await ctx.send("You didn't specify the raffle's name!")
		return

	raffle = await get_raffle_data()

	if name not in raffle:
		await ctx.send("That's not a valid raffle which is going on right now!")
		return

	if user == None:
		user = ctx.author

	if str(user.id) not in raffle[name]:
		await ctx.send("You didn't not enter that raffle!")
		return
		
	range1 = raffle[name][str(user.id)]["range1"]
	range2 = raffle[name][str(user.id)]["range2"] 
	ticketUsed = (range2 - range1) + 1
	await ctx.send(f"**{user.name}** has **{ticketUsed}** tickets in the **{name}** raffle!")

#totaltickets command
@client.command()
async def totaltickets(ctx, name = None):
	if name == None:
		await ctx.send("Please specify the name of the raffle next time!")
		return

	raffle = await get_raffle_data()

	if name not in raffle:
		await ctx.send("That's not a valid raffle which is going on right now!")
		return

	total = raffle["name"]["size"]
	await ctx.send(f"The **{name}** raffle has **{total}** tickets in total currently!")

#list command
@client.command()
async def list(ctx):
	raffle = await get_raffle_data()
	em = discord.Embed(title="Server's Raffles", color=ctx.author.color)

	for i in raffle:
		size = 0

		for x in raffle[i]:
			size += 1

		size -= 2

		prize = raffle[i]["prize"]
		channel = raffle[i]["channel"]
		em.add_field(name=i, value=f"**People Participated**: {size}\n**Prize**: {prize}\n**Channel**: <#{channel}>", inline=False)

	await ctx.send(embed=em)

#end command
@client.command()
async def end(ctx, name=None):
	if name == None:
		await ctx.send("Please specify the name of the raffle you want to end next time!")

	if ctx.author.id not in [756053421420707928, 796042231538122762, 740883324083503155, 905921030206414898]:
		await ctx.send("Sorry, but you don't have access to end a raffle! If this is a mistake plesae contact Hericulum#6785")
		return

	raffle = await get_raffle_data()

	if name not in raffle:
		await ctx.send("That's not a valid raffle going on right now!")

	if raffle[name]["channel"] != ctx.channel.id:
		channel = raffle[name]["channel"]
		await ctx.send(f"That raffle was not made in this channel! Please go to <#{channel}> and type the same command there inorder to end the raffle")
		return

	size = raffle[name]["size"]
	
	if size == 0:
		await ctx.send("No one won cause nobody joined the raffle!")
		await remove_raffle(name)
		return

	luckyNumber = random.randint(1, size)

	for i in raffle[name]:
		if i != 'size' and i != 'prize' and i != 'channel':
			range1 = raffle[name][i]["range1"]
			range2 = raffle[name][i]["range2"]

			if(range1 <= luckyNumber  and luckyNumber <= range2):
				prize = raffle[name]["prize"]
				await ctx.send(f"Congratulations <@!{int(i)}>! You just won the **{name}** raffle! The prize is: **{prize}**")
				await remove_raffle(name)
				return

#start command
@client.command()
async def start(ctx, name=None, *, prize=None):
	if ctx.author.id not in [756053421420707928, 796042231538122762, 740883324083503155, 905921030206414898]:
		await ctx.send("Sorry, but you don't have access to start a raffle! If this is a mistake plesae contact Hericulum#6785")
		return

	if name == None:
		await ctx.send("Please specify the name of the raffle you want to make next time!")
		return

	if prize == None:
		await ctx.send("Please specify the prize of the raffle you want to make next time!")
		return

	raffle = await get_raffle_data()

	if name in raffle:
		await ctx.send("That raffle name is already registered and is going on right now!")
		return

	for i in raffle:
		if raffle[i]["channel"] == ctx.channel.id:
			await ctx.send(f"A raffel named **{i}** is already going on in this channel!")
			return

	await open_raffle(name, prize, ctx.channel.id)
	await ctx.send(f"Successfully created a raffle in this channel, named **{name}** and the prize is **{prize}**")

#on_command_error error
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("That command is invalid")
        return

    raise error

keep_alive.keep_alive()
#run event
token = os.environ.get("Token")
client.run(token)	