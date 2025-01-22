import discord
from discord import app_commands
from discord.ext import commands
import datetime
import pytz
import json
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

DATA_FILE = 'attendance.json'

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

attendance_data = load_data(DATA_FILE)

@bot.event
async def on_ready():
    print(f'{bot.user} 출퇴근봇이 준비되었습니다!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name="출근", description="출근 시간을 기록합니다")
async def check_in(interaction: discord.Interaction):
    user = interaction.user
    kr_time = datetime.datetime.now(pytz.timezone('Asia/Seoul'))
    current_time = kr_time.strftime('%Y-%m-%d %H:%M:%S')
    
    if str(user.id) not in attendance_data:
        attendance_data[str(user.id)] = {'check_ins': [], 'check_outs': []}
    
    if len(attendance_data[str(user.id)]['check_ins']) > len(attendance_data[str(user.id)]['check_outs']):
        embed = discord.Embed(
            title="⚠️ 출근 실패",
            description=f"{user.mention}님은 이미 출근 상태입니다!",
            color=discord.Color.red()
        )
        embed.add_field(name="마지막 출근 시간", value=attendance_data[str(user.id)]['check_ins'][-1], inline=False)
        embed.set_footer(text="퇴근 먼저 해주세요!")
        await interaction.response.send_message(embed=embed)
        return
    
    attendance_data[str(user.id)]['check_ins'].append(current_time)
    save_data(attendance_data, DATA_FILE)
    
    embed = discord.Embed(
        title="✅ 출근 완료",
        description=f"{user.mention}님이 출근하셨습니다!",
        color=discord.Color.green()
    )
    embed.add_field(name="출근 시간", value=current_time, inline=False)
    embed.add_field(name="근무 상태", value="🟢 근무중", inline=False)
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="좋은 하루 보내세요! 🌟")

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="퇴근", description="퇴근 시간을 기록합니다")
async def check_out(interaction: discord.Interaction):
    user = interaction.user
    kr_time = datetime.datetime.now(pytz.timezone('Asia/Seoul'))
    current_time = kr_time.strftime('%Y-%m-%d %H:%M:%S')
    
    if str(user.id) not in attendance_data or len(attendance_data[str(user.id)]['check_ins']) <= len(attendance_data[str(user.id)]['check_outs']):
        embed = discord.Embed(
            title="⚠️ 퇴근 실패",
            description=f"{user.mention}님은 아직 출근하지 않으셨습니다!",
            color=discord.Color.red()
        )
        embed.set_footer(text="출근을 먼저 해주세요!")
        await interaction.response.send_message(embed=embed)
        return
    

    check_in_time = datetime.datetime.strptime(attendance_data[str(user.id)]['check_ins'][-1], '%Y-%m-%d %H:%M:%S')
    check_out_time = datetime.datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
    work_duration = check_out_time - check_in_time
    hours = work_duration.seconds // 3600
    minutes = (work_duration.seconds % 3600) // 60
    
    attendance_data[str(user.id)]['check_outs'].append(current_time)
    save_data(attendance_data, DATA_FILE)
    
    embed = discord.Embed(
        title="🏃 퇴근 완료",
        description=f"{user.mention}님이 퇴근하셨습니다!",
        color=discord.Color.blue()
    )
    embed.add_field(name="출근 시간", value=attendance_data[str(user.id)]['check_ins'][-1], inline=True)
    embed.add_field(name="퇴근 시간", value=current_time, inline=True)
    embed.add_field(name="근무 시간", value=f"{hours}시간 {minutes}분", inline=False)
    embed.add_field(name="근무 상태", value="🔴 퇴근완료", inline=False)
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="수고하셨습니다! 🌙")

    await interaction.response.send_message(embed=embed)

TOKEN = '여기에 봇토큰!'
bot.run(TOKEN)
