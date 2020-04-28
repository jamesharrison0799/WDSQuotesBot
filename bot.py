import discord
from PIL import Image, ImageDraw, ImageFont
import time
from quotemaker.quotemaker import ImageMaker
from discord.ext import commands
from configparser import ConfigParser

parser = ConfigParser()
parser.read('config.ini')

client = commands.Bot(command_prefix =parser.get('commands','command_prefix'))
client.remove_command('help')

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game("use .helpme for commands"))
    print('FUCKIN READY FOR IT M8')

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing requirements, pls use proper syntax")

@client.command(pass_context=True)
async def helpme(ctx):
    author = ctx.message.author
    #print("Sent help dm to "+author)
    await ctx.author.send('.quote "[NAME]" "[QUOTE]" / then attatch an image')
    await ctx.author.send('.quotelink "[NAME]" "[QUOTE]" [LINK]')

#author,quote(message),url
@client.command()
async def quotelink(ctx,author,quote,image_path):
    try:
        img = ImageMaker(author,quote,image_path)
        img.create_image()
        with open(img.last_image(),'rb') as f:
            await ctx.send(file=discord.File(f))
        print("{} created by {} in {}".format(img.last_image(), ctx.message.author, ctx.message.guild))
    except Exception as e:
        await ctx.send("Shite, somethings gone wrong")
        print(e)

@client.command()
async def quote(ctx,author,quote):
    try:
        url = ctx.message.attachments[0].url
        #file_request = requests.get(url)
        img = ImageMaker(author,quote,url)
        img.create_image()
        with open(img.last_image(),'rb') as f:
            await ctx.send(file=discord.File(f))
        print("{} created by {} in {}".format(img.last_image(), ctx.message.author, ctx.message.guild))
        del img
    except Exception as e:
        await ctx.send("Shite, somethings gone wrong")
        print(e)



try:
    client.run(parser.get('discord','token'))
except Exception as e:
    raise
