import random, os, sys
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid
from info import ADMINS, LOG_CHANNEL, PICS, SUPPORT_LINK, UPDATES_LINK, MELCOW_VID
from database.users_chats_db import db
from database.ia_filterdb import Media
from utils import get_size, temp, get_settings
from Script import script
from pyrogram.errors import ChatAdminRequired


@Client.on_chat_member_updated(filters.group)
async def welcome(bot, message):
    if message.new_chat_member and not message.old_chat_member:
        if message.new_chat_member.user.id == temp.ME:
            buttons = [[
                InlineKeyboardButton('ᴜᴘᴅᴀᴛᴇ', url=UPDATES_LINK),
                InlineKeyboardButton('ꜱᴜᴘᴘᴏʀᴛ', url=SUPPORT_LINK)
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            user = message.from_user.mention if message.from_user else "Dear"
            await bot.send_photo(
                chat_id=message.chat.id,
                photo=random.choice(PICS),
                caption=f"👋 Hello {user},\n\nThank you for adding me to the <b>'{message.chat.title}'</b> group, Don't forget to make me admin. If you want to know more ask the support group. 😘</b>",
                reply_markup=reply_markup
            )
            return
        
        settings = await get_settings(message.chat.id)
        if settings["welcome"]:
            for u in message.new_chat_members:
                if (temp.MELCOW).get('welcome') is not None:
                    try:
                        await (temp.MELCOW['welcome']).delete()
                    except:
                        pass
                temp.MELCOW['welcome'] = await message.reply_video(
                                                 video=(MELCOW_VID),
                                                 caption=(script.WELCOME_TEXT.format(u.mention, message.chat.title)),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=SUPPORT_LINK),
                         InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=UPDATES_LINK)],
                        [InlineKeyboardButton("Bᴏᴛ Oᴡɴᴇʀ", url="https://t.me/DAEMON99")]
                    ]
                ),
                parse_mode=enums.ParseMode.HTML
            )

            settings = await get_settings(message.chat.id)
            if settings["auto_delete"]:
                await asyncio.sleep(600)
                await temp.MELCOW['welcome'].delete()


@Client.on_message(filters.command('restart') & filters.user(ADMINS))
async def restart_bot(bot, message):
    msg = await message.reply("Restarting...")
    with open('restart.txt', 'w+') as file:
        file.write(f"{msg.chat.id}\n{msg.id}")
    os.execl(sys.executable, sys.executable, "bot.py")


@Client.on_message(filters.command('leave') & filters.user(ADMINS))
async def leave_a_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat ID')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason provided."
    try:
        chat = int(chat)
    except:
        chat = chat
    try:
        buttons = [[
            InlineKeyboardButton('Support Group', url=SUPPORT_LINK)
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat,
            text=f'Hello Friends,\nMy owner has told me to leave from group so i go! If you need add me again contact my support group.\nReason - <code>{reason}</code>',
            reply_markup=reply_markup,
        )
        await bot.leave_chat(chat)
        await message.reply(f"<b>✅️ Successfully bot left from this group - `{chat}`</b>")
    except Exception as e:
        await message.reply(f'Error - {e}')


@Client.on_message(filters.command('ban_grp') & filters.user(ADMINS))
async def disable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat ID')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason provided."
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give me a valid chat ID')
    cha_t = await db.get_chat(int(chat_))
    if not cha_t:
        return await message.reply("Chat not found in database")
    if cha_t['is_disabled']:
        return await message.reply(f"This chat is already disabled.\nReason - <code>{cha_t['reason']}</code>")
    await db.disable_chat(int(chat_), reason)
    temp.BANNED_CHATS.append(int(chat_))
    await message.reply('Chat successfully disabled')
    try:
        buttons = [[
            InlineKeyboardButton('Support Group', url=SUPPORT_LINK)
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat_, 
            text=f'Hello Friends,\nMy owner has told me to leave from group so i go! If you need add me again contact my support group.\nReason - <code>{reason}</code>',
            reply_markup=reply_markup)
        await bot.leave_chat(chat_)
    except Exception as e:
        await message.reply(f"Error - {e}")


@Client.on_message(filters.command('unban_grp') & filters.user(ADMINS))
async def re_enable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat ID')
    chat = message.command[1]
    try:
        chat_ = int(chat)
    except:
        return await message.reply('Give me a valid chat ID')
    sts = await db.get_chat(int(chat))
    if not sts:
        return await message.reply("Chat not found in database")
    if not sts.get('is_disabled'):
        return await message.reply('This chat is not yet disabled.')
    await db.re_enable_chat(int(chat_))
    temp.BANNED_CHATS.remove(int(chat_))
    await message.reply("Chat successfully re-enabled")


@Client.on_message(filters.command('invite_link') & filters.user(ADMINS))
async def gen_invite_link(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a chat ID')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        return await message.reply('Give me a valid chat ID')
    try:
        link = await bot.create_chat_invite_link(chat)
    except Exception as e:
        return await message.reply(f'Error - {e}')
    await message.reply(f'Here is your invite link: {link.invite_link}')


@Client.on_message(filters.command('ban_user') & filters.user(ADMINS))
async def ban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a user ID or Username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason provided."
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except Exception as e:
        return await message.reply(f'Error - {e}')
    else:
        if k.id in ADMINS:
            return await message.reply('You ADMINS')
        jar = await db.get_ban_status(k.id)
        if jar['is_banned']:
            return await message.reply(f"{k.mention} is already banned.\nReason - <code>{jar['ban_reason']}</code>")
        await db.ban_user(k.id, reason)
        temp.BANNED_USERS.append(k.id)
        await message.reply(f"Successfully banned {k.mention}")


@Client.on_message(filters.command('unban_user') & filters.user(ADMINS))
async def unban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a user ID or Username')
    r = message.text.split(None)
    if len(r) > 2:
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except Exception as e:
        return await message.reply(f'Error - {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if not jar['is_banned']:
            return await message.reply(f"{k.mention} is not banned.")
        await db.unban_user(k.id)
        temp.BANNED_USERS.remove(k.id)
        await message.reply(f"Successfully unbanned {k.mention}")
