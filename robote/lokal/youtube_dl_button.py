#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
LOGGER=logging.getLogger(__name__)
import asyncio
import json
import math
import os
import shutil
import time
import subprocess
from datetime import datetime
from robote import(DOWNLOAD_LOCATION,AUTH_CHANNEL)
import pyrogram
logging.getLogger("pyrogram").setLevel(logging.ERROR)
from robote.heroku.upload_tege import upload_tege,upload_to_gdrive
async def youtube_dl_call_back(bot,update):
 LOGGER.info(update)
 cb_data=update.data
 get_cf_name=update.message.caption
 cf_name=""
 if "|" in get_cf_name:
  cf_name=get_cf_name.split("|",maxsplit=1)[1]
  cf_name=cf_name.strip()
 tg_send_type,youtube_dl_format,youtube_dl_ext=cb_data.split("|")
 current_user_id=update.message.reply_to_message.from_user.id
 current_touched_user_id=update.from_user.id
 if current_user_id!=current_touched_user_id:
  await bot.answer_callback_query(callback_query_id=update.id,text="who are you? 🤪🤔🤔🤔",show_alert=True,cache_time=0)
  return False,None
 user_working_dir=os.path.join(DOWNLOAD_LOCATION,str(current_user_id))
 if not os.path.isdir(user_working_dir):
  await bot.delete_messages(chat_id=update.message.chat.id,message_ids=[update.message.message_id,update.message.reply_to_message.message_id,],revoke=True)
  return
 save_ytdl_json_path=user_working_dir+ "/"+str("ytdleech")+".json"
 try:
  with open(save_ytdl_json_path,"r",encoding="utf8")as f:
   response_json=json.load(f)
  os.remove(save_ytdl_json_path)
 except(FileNotFoundError)as e:
  await bot.delete_messages(chat_id=update.message.chat.id,message_ids=[update.message.message_id,update.message.reply_to_message.message_id,],revoke=True)
  return False
 response_json=response_json[0]
 youtube_dl_url=response_json.get("webpage_url")
 LOGGER.info(youtube_dl_url)
 custom_file_name="%(title)s.%(ext)s"
 LOGGER.info(custom_file_name)
 await update.message.edit_caption(caption="trying to download")
 description="@PublicLeech"
 if "fulltitle" in response_json:
  description=response_json["fulltitle"][0:1021]
 tmp_directory_for_each_user=os.path.join(DOWNLOAD_LOCATION,str(update.message.message_id))
 if not os.path.isdir(tmp_directory_for_each_user):
  os.makedirs(tmp_directory_for_each_user)
 download_directory=tmp_directory_for_each_user
 LOGGER.info(download_directory)
 download_directory=os.path.join(tmp_directory_for_each_user,custom_file_name)
 LOGGER.info(download_directory)
 command_to_exec=[]
 if tg_send_type=="audio":
  command_to_exec=["youtube-dl","-c","--prefer-ffmpeg","--extract-audio","--audio-format",youtube_dl_ext,"--audio-quality",youtube_dl_format,youtube_dl_url,"-o",download_directory,]
 else:
  minus_f_format=youtube_dl_format
  if "youtu" in youtube_dl_url:
   for for_mat in response_json["formats"]:
    format_id=for_mat.get("format_id")
    if format_id==youtube_dl_format:
     acodec=for_mat.get("acodec")
     vcodec=for_mat.get("vcodec")
     if acodec=="none" or vcodec=="none":
      minus_f_format=youtube_dl_format+"+bestaudio"
     break
  command_to_exec=["youtube-dl","-c","--embed-subs","-f",minus_f_format,"--hls-prefer-ffmpeg",youtube_dl_url,"-o",download_directory,]
 command_to_exec.append("--no-warnings")
 command_to_exec.append("--restrict-filenames")
 if "hotstar" in youtube_dl_url:
  command_to_exec.append("--geo-bypass-country")
  command_to_exec.append("IN")
 LOGGER.info(command_to_exec)
 start=datetime.now()
 process=await asyncio.create_subprocess_exec(*command_to_exec,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE,)
 stdout,stderr=await process.communicate()
 e_response=stderr.decode().strip()
 t_response=stdout.decode().strip()
 ad_string_to_replace="please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call youtube-dl with the --verbose flag and include its complete output."
 if e_response and ad_string_to_replace in e_response:
  error_message=e_response.replace(ad_string_to_replace,"")
  await update.message.edit_caption(caption=error_message)
  return False,None
 if t_response:
  end_one=datetime.now()
  time_taken_for_download=(end_one-start).seconds
  dir_contents=len(os.listdir(tmp_directory_for_each_user))
  await update.message.edit_caption(caption=f"found {dir_contents} files")
  user_id=update.from_user.id
  LOGGER.info(tmp_directory_for_each_user)
  for a,b,c in os.walk(tmp_directory_for_each_user):
   LOGGER.info(a)
   for d in c:
    e=os.path.join(a,d)
    LOGGER.info(e)
    gaut_am=os.path.basename(e)
    LOGGER.info(gaut_am)
    fi_le=e
    if cf_name:
     fi_le=os.path.join(a,cf_name)
     LOGGER.info(fi_le)
     os.rename(e,fi_le)
     gaut_am=os.path.basename(fi_le)
     LOGGER.info(gaut_am)
  G_DRIVE=False
  txt=update.message.reply_to_message.text
  print(txt)
  g_txt=txt.split()
  print(g_txt)
  if len(g_txt)>1:
   if g_txt[1]=="gdrive":
    G_DRIVE=True
  if G_DRIVE:
   liop=subprocess.Popen(["mv",f'{fi_le}',"/opt/"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   out,err=liop.communicate()
   LOGGER.info(out)
   LOGGER.info(err)
   final_response=await upload_to_gdrive(gaut_am,update.message,update.message.reply_to_message,user_id)
  else:
   final_response=await upload_tege(update.message,tmp_directory_for_each_user,user_id,{},True)
  '''  
        final_response = await upload_tege(update.message, tmp_directory_for_each_user, user_id, {}, True )
        '''  
  LOGGER.info(final_response)
  try:
   shutil.rmtree(tmp_directory_for_each_user)
  except:
   pass