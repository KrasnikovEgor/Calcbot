import discord
import asyncio
from discord.ext import commands
from sympy import *
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

zn = '+-=></*\n},'
cfr = '0123456789.'


def preobr(a):
    a = a.replace(' ', '')
    a = a.replace('^', '**')
    a = a.replace('log', ' - - - - - - - - -')
    a = a.replace('asin', ' - - - - - - - -')
    a = a.replace('acos', ' - - - - - - -')
    a = a.replace('atag', ' - - - - - -')
    a = a.replace('acot', ' - - - - -')
    a = a.replace('sin', ' - - - -')
    a = a.replace('cos', ' - - -')
    a = a.replace('tan', ' - -')
    a = a.replace('cot', ' -')
    a = a.replace('×', '*')
    s = 0
    i = 0
    while i < len(a):
        if a[i] == '√':
            k = '**(1/2)'
            if i != 0 and a[i - 1] == '}':
                g = i - 2
                h = 1
                while h != 0:
                    if a[g] == '}':
                        h += 1
                    elif a[g] == '{':
                        h -= 1
                    g -= 1
                k = '**(1/(' + a[g + 2:i - 1] + '))'
                a = a[:g + 1] + a[i + 1:]
                i -= len(k) - 6
            else:
                a = a[:i] + a[i + 1:]
            if a[i] == '(':
                g = i + 1
                h = 1
                while h != 0:
                    if a[g] == '(':
                        h += 1
                    elif a[g] == ')':
                        h -= 1
                    g += 1
            else:
                g = i + 1
                while a[g] in cfr and a[i] in cfr + '-':
                    g += 1
            a = a[:g] + k + a[g:]
        i += 1
    for j in range(len(a)):
        i = j + s
        if a[i] == "'" and a[i - 1] != ')':
            g = i
            while a[g] not in zn:
                g -= 1
            a = a[:g + 1] + 'diff(' + a[g + 1:i] + ')' + a[i + 1:]
            s += 5
        elif a[i] == "'" and a[i - 1] == ')':
            g = i - 2
            h = 1
            while h != 0:
                if a[g] == ')':
                    h += 1
                elif a[g] == '(':
                    h -= 1
                g -= 1
            a = a[:g + 1] + 'diff' + a[g + 1:i] + a[i + 1:]
            s += 3
        if (i + 1 != len(a) and a[i] not in zn + '({' and
        a[i + 1] not in zn + ")'" and (a[i] not in cfr or a[i + 1] not in cfr)):
            a = a[:i + 1] + '*' + a[i + 1:]
            s += 1
    a = a.replace(' - - - - - - - - -', 'log')
    a = a.replace(' - - - - - - - -', 'asin')
    a = a.replace(' - - - - - - -', 'acos')
    a = a.replace(' - - - - - -', 'atan')
    a = a.replace(' - - - - -', 'acot')
    a = a.replace(' - - - -', 'sin')
    a = a.replace(' - - -', 'cos')
    a = a.replace(' - -', 'tan')
    a = a.replace(' -', 'cot')
    a = a.replace('π', 'pi')
    return a


class Calcbot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(
            f'Привет, {member.name}! Чтобы узнать мои возможности, введи команду "#!help_me".'
        )

    @commands.command(name='calculate')
    async def calculate(self, ctx, arg):
        a = arg
        if len(a) != 0:
            try:
                a = preobr(a).split('\n')
                if len(a) == 1 and '=' not in a[0] and '>' not in a[0] and '<' not in a[0]:
                    a = expand(simplify(a[0]))
                    await ctx.send((pretty(a)).replace('⋅', '×'))
                else:
                    for i in range(len(a)):
                        if a[i].count('=') == 1 and a[i].count('>') == 0 and a[i].count('<') == 0:
                            a[i] = simplify(a[i].replace('=', '-(') + ')')
                        else:
                            a[i] = simplify(a[i])
                    else:
                        t = True
                        a = solve(a, set=True)
                        if type(a) == tuple and len(a) != 0:
                            a = (a[0], list(a[1]))
                            i = 0
                            while i < len(a[1]):
                                if 'I' in str(a[1][i]):
                                    del a[1][i]
                                    i -= 1
                                i += 1
                            if len(a[0]) == 1:
                                a = (a[0][0], a[1])
                            if len(a[1]) == 1:
                                a = (a[0], list(a[1])[0])
                            elif len(list(a[1])[0]) == 1:
                                a = (a[0], list(a[1]))
                                for i in range(len(a[1])):
                                    a[1][i] = list(a[1][i])[0]
                                a = (a[0], set(a[1]))
                            if len(a[1]) == 1:
                                a = (a[0], list(a[1])[0])
                        if a != [] and t:
                            await ctx.send((pretty(a)).replace('⋅', '×'))
                        else:
                            pass
            except Exception:
                print(a)
                await ctx.send('НЕКОРЕКТНЫЙ ВВОД')

    @commands.command(name='help_me')
    async def help_me(self, ctx):
        with open('data/help.txt', mode='r',  encoding="utf8") as helpfile:
            await ctx.send(''.join(helpfile.readlines()))


intents = discord.Intents.all()
intents.members = True
intents.message_content = True
TOKEN = open('data/token.txt', mode='r',  encoding="utf8").readline()
bot = commands.Bot(command_prefix='#!', intents=intents)


async def main():
    await bot.add_cog(Calcbot(bot))
    await bot.start(TOKEN)


asyncio.run(main())