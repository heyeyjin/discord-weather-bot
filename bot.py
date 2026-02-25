import discord
from discord.ext import commands, tasks
import aiohttp
import datetime
import os
from dotenv import load_dotenv

# .env 로드
load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
TARGET_USER_ID = int(os.getenv('TARGET_USER_ID'))

# 날씨 데이터 가져오기
async def get_weather():
    lat = 37.57
    lon = 126.98
    api_key = WEATHER_API_KEY
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&lang=kr&units=metric"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                data = await response.json()

    temp = int(data['main']['temp'])
    description = data['weather'][0]['description']
    city = data['name']

    if "Seoul" in city:
        display_name = "서울"

    return f"{display_name}의 현재 기온은 섭씨 {temp}도, 날씨는 {description}입니다."

# 봇 객체 생성 (명령어 시작 문자를 '!'로 설정)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 한국시간 오전 9시
KST = datetime.timezone(datetime.timedelta(hours=9))
target_time = datetime.time(hour=9, minute=0, tzinfo=KST)

# DM 자동 알림
@tasks.loop(time = target_time)
async def daily_weather():
    user = await bot.fetch_user(TARGET_USER_ID)
    weather_info = await get_weather()
    await user.send(f"🌅[오늘의 날씨]\n{weather_info}")

# 봇이 준비되었을 때 이벤트 실행
@bot.event
async def on_ready():
    print(f"{bot.user.name} 로그인 성공!")

    if not daily_weather.is_running(): 
            daily_weather.start()

# 수동으로 날씨 정보 가져옴(!날씨 명령어)
@bot.command()
async def 날씨(ctx):
    info = await get_weather()
    await ctx.send(info)    

# 봇 실행
bot.run(DISCORD_TOKEN)