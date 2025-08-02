import discord
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# Discord 토큰 가져오기
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

print("=== Discord 봇 테스트 시작 ===")
print(f"토큰이 로드되었나요? {DISCORD_TOKEN is not None}")

if not DISCORD_TOKEN:
    print("❌ DISCORD_TOKEN이 .env 파일에 없습니다!")
    print("✅ .env 파일을 확인해주세요")
    exit()

# 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'✅ 봇 로그인 성공!')
    print(f'봇 이름: {bot.user.name}')
    print(f'봇 ID: {bot.user.id}')
    print(f'연결된 서버 수: {len(bot.guilds)}')
    
    # 연결된 서버 목록 출력
    for guild in bot.guilds:
        print(f'  - {guild.name} (ID: {guild.id})')
    
    print("=== 테스트 완료! Ctrl+C로 종료하세요 ===")

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"❌ 오류 발생: {event}")
    import traceback
    traceback.print_exc()

# 봇 실행
try:
    print("🚀 봇 시작 중...")
    bot.run(DISCORD_TOKEN)
except discord.LoginFailure:
    print("❌ 로그인 실패! 토큰을 확인해주세요.")
except Exception as e:
    print(f"❌ 예상치 못한 오류: {e}")
    import traceback
    traceback.print_exc()