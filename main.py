'''
    Liberation - Party voice channels, made easier
    by jbcarreon123 and Gowthr
    Copyright (C) 2024
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import os
import uuid
from time import sleep

import yaml
import disnake
import logging
from sqlite4 import SQLite4
from disnake.ext import commands
from config import Config
from icons import Icons
from message import Message


def load_config():
    file_path = os.path.dirname(os.path.realpath(__file__)) + "\\config.yml"
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            config_data = yaml.safe_load(file)
        return Config(**config_data)
    else:
        logging.critical('Configuration does not exist. Exiting...')
        exit(-1)


def find_easter_egg_by_code(target_code):
    file_path = os.path.dirname(os.path.realpath(__file__)) + "\\ee.yml"
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            ee_data_safe = yaml.safe_load(file)
    for es in ee_data_safe:
        if es['code'] == target_code:
            return es
    return None


config = load_config()
bot = commands.AutoShardedBot(command_prefix=config.Prefix,
                              intents=disnake.Intents.default() | disnake.Intents.message_content)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s')
database = SQLite4("LiberaDB.db")
database.connect()

database.create_table("config", ["guildId", "categoryId", "createPartyVcId"])
database.create_table("party", ["guildId", "partyId", "ownerId", "channelId"])


def get_random_str():
    return str(uuid.uuid4()).split("-")[0]


def if_party_exists(*, user: int = None, party: str = None):
    if user is None:
        pa = database.select("party", ["partyId"], condition=f'partyId = {party}')
        return pa is not None and len(pa) is not 0
    else:
        pa = database.select("party", ["ownerId"], condition=f'ownerId = {user}')
        return pa is not None and len(pa) is not 0


def get_icons():
    file_path = os.path.dirname(os.path.realpath(__file__)) + "\\icons.yml"
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            icon_data = yaml.safe_load(file)
        return Icons(**icon_data)
    else:
        logging.warning('Cannot find icons.yml. Will not put emojis in buttons.')
        return None


def create_guild_config_msg(guild: disnake.Guild) -> Message:
    embed = disnake.Embed(title=f'Guild Configuration')
    icons = get_icons()
    compo = [
    ]
    return Message(embed=embed, buttons=compo)


def create_party_config_msg(channel: disnake.VoiceChannel) -> Message:
    embed = disnake.Embed(title=f'Control Panel for #{channel.name}')
    icons = get_icons()
    compo = [
        [
            disnake.ui.Button(label="{status}".format(
                status="Unlocked" if channel.permissions_for(channel.guild.default_role).connect == True else "Locked"),
                              emoji="{emoji}".format(emoji="" if icons is None else "<:{icon}:{id}>".format(
                                  icon=icons.unlock['name'] if channel.permissions_for(
                                      channel.guild.default_role).connect is True else icons.lock['name'],
                                  id=icons.unlock['id'] if channel.permissions_for(
                                      channel.guild.default_role).connect is True else icons.lock['id'])),
                              custom_id="liberation.party.toggle_lock", style=disnake.ButtonStyle.danger),
            disnake.ui.Button(label="{visible}".format(visible="Public" if channel.permissions_for(
                channel.guild.default_role).view_channel == True else "Private"),
                              emoji="{emoji}".format(emoji="" if icons is None else "<:{icon}:{id}>".format(
                                  icon=icons.public['name'] if channel.permissions_for(
                                      channel.guild.default_role).connect is True else icons.private['name'],
                                  id=icons.public['id'] if channel.permissions_for(
                                      channel.guild.default_role).connect is True else icons.private['id'])),
                              custom_id="liberation.party.toggle_visibility", style=disnake.ButtonStyle.danger),
            disnake.ui.Button(label="Add Members", emoji=f"<:{icons.add_members['name']}:{icons.add_members['id']}>",
                              custom_id="liberation.party.add_members",
                              style=disnake.ButtonStyle.success,
                              disabled=(channel.permissions_for(channel.guild.default_role).connect is True))
        ],
        [
            disnake.ui.Button(label="Set User Limit",
                              emoji=f"<:{icons.set_user_limit['name']}:{icons.set_user_limit['id']}>",
                              custom_id="liberation.party.set_user_limit",
                              style=disnake.ButtonStyle.blurple),
            disnake.ui.Button(label="Set Permissions",
                              emoji=f"<:{icons.set_permissions['name']}:{icons.set_permissions['id']}>",
                              custom_id="liberation.party.set_permissions",
                              style=disnake.ButtonStyle.blurple),
            disnake.ui.Button(label="Set Party VC Name",
                              emoji=f"<:{icons.set_vc_name['name']}:{icons.set_vc_name['id']}>",
                              custom_id="liberation.party.set_vc_name",
                              style=disnake.ButtonStyle.blurple)
        ],
        [
            disnake.ui.Button(label="Set Slowmode",
                              emoji=f"<:{icons.set_slowmode['name']}:{icons.set_slowmode['id']}>",
                              custom_id="liberation.party.set_slowmode",
                              style=disnake.ButtonStyle.blurple),
            disnake.ui.Button(label="Set Voice Region",
                              emoji=f"<:{icons.set_voice_region['name']}:{icons.set_voice_region['id']}>",
                              custom_id="liberation.party.set_voice_region",
                              style=disnake.ButtonStyle.blurple),
            disnake.ui.Button(label="Set Bitrate",
                              emoji=f"<:{icons.set_user_limit['name']}:{icons.set_user_limit['id']}>",
                              custom_id="liberation.party.set_bitrate",
                              style=disnake.ButtonStyle.blurple)
        ],
        [
            disnake.ui.Button(label="Disband Party",
                              emoji=f"<:{icons.disband['name']}:{icons.disband['id']}>",
                              custom_id="liberation.party.disband",
                              style=disnake.ButtonStyle.danger)
        ]
    ]
    return Message(embed=embed, buttons=compo)


@bot.event
async def on_ready():
    for x in range(0, bot.shard_count - 1):
        p = disnake.Activity(name=config.Presence['Name'], state=config.Presence['State'] + f'\nShard ID: {x}',
                             type=config.Presence['Type'])
        await bot.change_presence(status=disnake.Status.online, activity=p, shard_id=x)
    logging.info(f'Bot ready! Logged in as {bot.user.name}.')


@bot.event
async def on_voice_state_update(member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
    if after is None:
        return
    categories = database.select("config", columns=['guildId', 'createPartyVcId'],
                                 condition=f'guildId = {member.guild.id}')
    vcId = categories[0][1]
    if after.channel.id == vcId:
        if if_party_exists(user=member.id):
            chnl = member.guild.get_channel(vcId)
            msg = await chnl.send(
                f'You already have a party, {member.mention}! Please delete the existing party first.')
            await msg.delete(delay=5)
            return
        categories = database.select("config", columns=['guildId', 'categoryId'],
                                     condition=f'guildId = {member.guild.id}')
        category = categories[0][1]
        vc = await member.guild.create_voice_channel(name=member.name + "'s Party",
                                                     category=member.guild.get_channel(category))
        rnd = get_random_str()
        database.insert("party", {"guildId": member.guild.id, "partyId": rnd, "ownerId": member.id, "channelId": vc.id})
        await vc.send(f"{member.mention} Here you go! Party ID is {rnd}!")
        await member.move_to(vc, reason='Created party VC')
        await vc.send(embed=msg.embed, components=msg.buttons)


# TODO: Write help command
@bot.slash_command(name='help', description='Command Explanation')
async def help_slash(inr: disnake.ApplicationCommandInteraction):
    embed = disnake.Embed(title="Commands")
    for cmd in bot.global_slash_commands:
        embed.add_field(f'</{cmd.name}:{cmd.id}>', f'{cmd.description}', inline=True)
    await inr.send(embed=embed)


@bot.slash_command(name='test', description='placeholder')
async def test(inr: disnake.ApplicationCommandInteraction, vc: disnake.VoiceChannel):
    msg = create_party_config_msg(vc)
    await inr.response.send_message(embed=msg.embed, components=msg.buttons)


@bot.slash_command(name='ping', description='Ping')
async def ping_slash(inr: disnake.ApplicationCommandInteraction):
    embed = disnake.Embed(title="Ping")
    embed.add_field('Shard Latency', f'{(bot.get_shard(inr.guild.shard_id).latency * 1000).__round__(2)}ms',
                    inline=True)
    embed.add_field('API Latency', f'{(bot.latency * 1000).__round__(2)}ms', inline=True)
    embed.set_footer(text=f'Shard {inr.guild.shard_id}/{bot.shard_count} • {len(bot.guilds)} guilds')
    await inr.response.send_message(embed=embed)


@bot.slash_command(name='shards', description='Get shards info')
async def shards_prefix(inr: disnake.ApplicationCommandInteraction):
    embed = disnake.Embed(title="Shards")
    embed.set_footer(text="Legend: 🟩 Online, 🟧 Rate Limited, 🟥 Disconnected")
    shard_id = ""
    shard_status = ""
    shard_ping = ""
    for x in range(0, bot.shard_count - 1):
        shard_id += f'Shard {x}\n'
        if bot.shards[x].is_closed():
            shard_status += '🟥\n'
        elif bot.shards[x].is_ws_ratelimited():
            shard_status += '🟧\n'
        else:
            shard_status += '🟩\n'
        shard_ping += f'{(bot.shards[x].latency * 1000).__round__(2)}ms\n'
    embed.add_field(name="Shard ID", value=shard_id, inline=True)
    embed.add_field(name="Status", value=shard_status, inline=True)
    embed.add_field(name="Latency", value=shard_ping, inline=True)
    await inr.response.send_message(embed=embed, reference=inr.message,
                                    allowed_mentions=disnake.AllowedMentions.none())


@bot.slash_command(name='configure', description='Configure the bot')
async def conf_slash(inr: disnake.ApplicationCommandInteraction, category: disnake.CategoryChannel):
    vc = await category.create_voice_channel(name='Create a Party')
    database.insert("config", {"guildId": inr.guild_id, "categoryId": category.id, "createPartyVcId": vc.id})
    await inr.response.send_message('<:done:1189216626604769320> Done and Done!')


@bot.slash_command(name='party', description='Party Slash Commands')
async def party(inr: disnake.ApplicationCommandInteraction):
    pass


@party.sub_command(name='create', description='Create a party VC')
async def create_party(inr: disnake.ApplicationCommandInteraction, display_name: str):
    await inr.response.send_message(
        '<:pending:1189216631268843530> Creating a party VC...\n<:desc:1189216629519826975> Administrators or people '
        'that have the `ADMINISTRATOR` permission can see party VCs, regardless of its privacy level!')
    categories = database.select("config", columns=['guildId', 'categoryId'], condition=f'guildId = {inr.guild_id}')
    category = categories[0][1]
    vc = await inr.guild.create_voice_channel(name=display_name + ' (Party)', category=inr.guild.get_channel(category))
    rnd = get_random_str()
    database.insert("party", {"guildId": inr.guild_id, "partyId": rnd, "ownerId": inr.user.id,
                                    "channelId": vc.id})
    await inr.edit_original_message(f'<:done:1189216626604769320> Done! Your Party ID is {rnd}!')
    msg = create_party_config_msg(vc)
    await vc.send(embed=msg.embed, components=msg.buttons)
    
    
@party.sub_command(name='disband', description='Disband a party VC')
async def disband_party(inr: disnake.ApplicationCommandInteraction, party_id: str):
    if (if_party_exists(party=party_id)):
        pa = database.select("party", ["partyId", "channelId"], condition=f'partyId = {party_id}')
        ch = pa[0][1]
        await inr.guild.get_channel(ch).delete(reason="Party disbanded.")
        database.delete("party", condition=f'partyId = {party_id}')
        await inr.response.send_message(f"Party `{party_id}` disbanded successfully.")
    else:
        await inr.response.send_message(f"Cannot find `{party_id}` on the database!")        


@bot.slash_command(name='about', description='About Liberation')
async def about(inr: disnake.ApplicationCommandInteraction):
    libera = disnake.Embed()
    libera.set_image(url='https://cdn.discordapp.com/attachments/1190294730358145024/1190305545446498355' +
                         '/Liberation_BannerU.png')
    embed = disnake.Embed(title='Liberation', description='Liberation is a bot that you can use to effortlessly '
                                                          'create temporary VCs.')
    embed.add_field('The Libera-Team',
                    '**[jbcarreon123](https://github.com/jbcarreon123)** *(Lead Developer)*\n**[Gowthr](https://github.com/gowthr)** *(Lead Developer & Designer)*\n**[MooreGaming1324](https://github.com/MooreGaming1324)** *(Administrator)*',
                    inline=True)
    embed.add_field('Links', '[GitHub Repo](https://github.com/liberation-dev/Liberation)\n', inline=True)
    await inr.response.send_message(embeds=[libera, embed])


@bot.slash_command(name='ee', description='idk')
async def ee(inr: disnake.ApplicationCommandInteraction, code: str):
    egg = find_easter_egg_by_code(code)
    if egg is not None:
        await inr.response.send_message(egg['content'])
    else:
        await inr.response.send_message('null')
        await inr.delete_original_message()


@bot.slash_command(name='change-pronouns', description='internal use only')
async def chprn(inr: disnake.AppCommandInteraction, pronoun: str):
    await bot.http.edit_my_member(inr.guild_id, pronouns=pronoun)
    await inr.response.send_message('done')


bot.run(config.Token)
