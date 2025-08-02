import discord
from discord.ext import commands, tasks
import requests
import random
import json
import re
from datetime import datetime
import os
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

# 설정값들 (.env 파일에서 가져오기)
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
PLAYLIST_ID = os.getenv('PLAYLIST_ID')
CHANNEL_ID = int(os.getenv('CHANNEL_ID')) if os.getenv('CHANNEL_ID') else None
GUILD_ID = int(os.getenv('GUILD_ID')) if os.getenv('GUILD_ID') else None

# 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

class MusicBot:
    def __init__(self, bot):
        self.bot = bot
        self.songs_history = []
        
    def clean_artist_name(self, artist):
        """아티스트명에서 불필요한 부분 제거"""
        clean_artist = artist
        clean_artist = re.sub(r'\s*-\s*Topic\s*$', '', clean_artist, flags=re.IGNORECASE)
        clean_artist = re.sub(r'\s*-\s*Official.*$', '', clean_artist, flags=re.IGNORECASE) 
        clean_artist = re.sub(r'\s*Official.*$', '', clean_artist, flags=re.IGNORECASE)
        clean_artist = re.sub(r'\s*-\s*VEVO\s*$', '', clean_artist, flags=re.IGNORECASE)
        return clean_artist.strip()
        
    def get_playlist_songs(self):
        """YouTube 재생목록에서 곡 목록 가져오기"""
        try:
            url = "https://www.googleapis.com/youtube/v3/playlistItems"
            all_songs = []
            next_page_token = None
            
            while True:
                params = {
                    'part': 'snippet',
                    'playlistId': PLAYLIST_ID,
                    'key': YOUTUBE_API_KEY,
                    'maxResults': 50
                }
                
                if next_page_token:
                    params['pageToken'] = next_page_token
                
                response = requests.get(url, params=params)
                data = response.json()
                
                if 'items' not in data:
                    print(f"API 응답 오류: {data}")
                    break
                
                for item in data['items']:
                    snippet = item['snippet']
                    title = snippet['title']
                    channel_title = snippet.get('videoOwnerChannelTitle', 'Unknown')
                    video_id = snippet['resourceId']['videoId']
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                    
                    if title != "Deleted video" and title != "Private video":
                        all_songs.append({
                            'title': title,
                            'artist': channel_title,
                            'url': video_url
                        })
                
                next_page_token = data.get('nextPageToken')
                if not next_page_token:
                    break
            
            return all_songs
            
        except Exception as e:
            print(f"YouTube API 오류: {e}")
            return []
    
    def select_random_song(self, songs):
        """중복되지 않게 랜덤 곡 선택"""
        if len(self.songs_history) >= len(songs) * 0.8:
            self.songs_history = []
        
        available_songs = [song for song in songs if song['title'] not in self.songs_history]
        
        if not available_songs:
            available_songs = songs
            self.songs_history = []
        
        selected_song = random.choice(available_songs)
        self.songs_history.append(selected_song['title'])
        
        return selected_song
    
    async def update_bot_nickname(self, song_title, artist):
        """봇 닉네임을 현재 곡과 아티스트로 변경"""
        try:
            guild = self.bot.get_guild(GUILD_ID)
            if guild:
                bot_member = guild.get_member(self.bot.user.id)
                if bot_member:
                    clean_artist = self.clean_artist_name(artist)
                    nickname = f"🎵 {song_title} - {clean_artist}"
                    
                    if len(nickname) > 32:
                        max_song_length = 32 - len(f"🎵  - {clean_artist}")
                        if max_song_length > 5:
                            short_title = song_title[:max_song_length-3] + "..."
                            nickname = f"🎵 {short_title} - {clean_artist}"
                        else:
                            available_length = 32 - len("🎵  - ...")
                            song_length = min(len(song_title), available_length // 2)
                            artist_length = available_length - song_length - 3
                            
                            short_title = song_title[:song_length] + ("..." if len(song_title) > song_length else "")
                            short_artist = clean_artist[:artist_length] + ("..." if len(clean_artist) > artist_length else "")
                            nickname = f"🎵 {short_title} - {short_artist}"
                    
                    await bot_member.edit(nick=nickname)
                    print(f"봇 닉네임 변경: {nickname}")
        except Exception as e:
            print(f"닉네임 변경 오류: {e}")
    
    async def send_daily_song(self):
        """매일 새로운 곡을 채널에 전송"""
        try:
            songs = self.get_playlist_songs()
            if not songs:
                print("재생목록에서 곡을 가져올 수 없습니다.")
                return None
            
            selected_song = self.select_random_song(songs)
            
            channel = self.bot.get_channel(CHANNEL_ID)
            if channel:
                clean_artist = self.clean_artist_name(selected_song['artist'])
                
                embed = discord.Embed(
                    title="🎵 오늘의 곡",
                    description=f"**{selected_song['title']}**",
                    color=0xFF6B6B,
                    timestamp=datetime.now()
                )
                embed.add_field(name="아티스트", value=clean_artist, inline=True)
                embed.add_field(name="링크", value=f"[YouTube에서 듣기]({selected_song['url']})", inline=True)
                embed.set_footer(text="매일 새로운 곡을 추천해드려요!")
                
                await channel.send(embed=embed)
                print(f"오늘의 곡 전송 완료: {selected_song['title']} - {clean_artist}")
                
                await self.update_bot_nickname(selected_song['title'], selected_song['artist'])
                
                return selected_song
            else:
                print(f"채널을 찾을 수 없습니다. 채널 ID: {CHANNEL_ID}")
                return None
            
        except Exception as e:
            print(f"일일 곡 전송 오류: {e}")
            return None

# 봇 인스턴스 생성
music_bot = MusicBot(bot)

@bot.event
async def on_ready():
    print(f'✅ {bot.user}가 로그인했습니다!')
    print(f'서버 수: {len(bot.guilds)}')
    
    for guild in bot.guilds:
        print(f'  - {guild.name} (ID: {guild.id})')
    
    if not daily_song_task.is_running():
        daily_song_task.start()
        print("⏰ 일일 음악 업데이트 작업이 시작되었습니다!")

@bot.event
async def on_command_error(ctx, error):
    print(f"명령어 오류 발생: {error}")
    await ctx.send(f"오류가 발생했습니다: {error}")

@bot.command(name='오늘의곡')
async def today_song(ctx):
    """수동으로 오늘의 곡 가져오기"""
    await ctx.send("🎵 새로운 곡을 찾고 있어요...")
    song = await music_bot.send_daily_song()
    if not song:
        await ctx.send("❌ 곡을 가져오는데 실패했습니다.")

@bot.command(name='재생목록')
async def playlist_info(ctx, page: int = 1):
    """재생목록 정보 확인 (페이지별로 표시)"""
    songs = music_bot.get_playlist_songs()
    if not songs:
        await ctx.send("❌ 재생목록을 불러올 수 없습니다.")
        return
    
    # 페이지네이션 설정
    songs_per_page = 10
    total_pages = (len(songs) + songs_per_page - 1) // songs_per_page
    page = max(1, min(page, total_pages))
    
    start_idx = (page - 1) * songs_per_page
    end_idx = start_idx + songs_per_page
    page_songs = songs[start_idx:end_idx]
    
    embed = discord.Embed(
        title="📁 연동된 재생목록",
        description=f"총 **{len(songs)}**곡 | 페이지 {page}/{total_pages}",
        color=0x4ECDC4
    )
    
    # 곡 목록을 클릭 가능한 링크로 표시
    song_list = []
    for i, song in enumerate(page_songs, start=start_idx + 1):
        clean_artist = music_bot.clean_artist_name(song['artist'])
        
        title = song['title']
        if len(title) > 40:
            title = title[:37] + "..."
        
        song_list.append(f"`{i:2d}.` [{title}]({song['url']}) - **{clean_artist}**")
    
    embed.add_field(name="🎵 곡 목록", value="\n".join(song_list), inline=False)
    
    # 페이지 네비게이션 안내
    if total_pages > 1:
        prev_page = page - 1 if page > 1 else total_pages
        next_page = page + 1 if page < total_pages else 1
        embed.add_field(
            name="📄 페이지 이동", 
            value=f"`!재생목록 {prev_page}` (이전) | `!재생목록 {next_page}` (다음)", 
            inline=False
        )
    
    embed.set_footer(text="💡 곡 제목을 클릭하면 YouTube에서 바로 들을 수 있어요!")
    await ctx.send(embed=embed)

@bot.command(name='검색')
async def search_song(ctx, *, query):
    """재생목록에서 곡 검색"""
    songs = music_bot.get_playlist_songs()
    if not songs:
        await ctx.send("❌ 재생목록을 불러올 수 없습니다.")
        return
    
    # 검색어로 곡 필터링
    query_lower = query.lower()
    matching_songs = []
    
    for song in songs:
        clean_artist = music_bot.clean_artist_name(song['artist'])
        
        if (query_lower in song['title'].lower() or 
            query_lower in clean_artist.lower()):
            matching_songs.append({**song, 'clean_artist': clean_artist})
    
    if not matching_songs:
        await ctx.send(f"🔍 '{query}'에 대한 검색 결과가 없습니다.")
        return
    
    embed = discord.Embed(
        title=f"🔍 '{query}' 검색 결과",
        description=f"**{len(matching_songs)}**곡을 찾았습니다.",
        color=0xFFD93D
    )
    
    results = []
    for i, song in enumerate(matching_songs[:10], 1):
        title = song['title']
        if len(title) > 35:
            title = title[:32] + "..."
        
        results.append(f"`{i:2d}.` [{title}]({song['url']}) - **{song['clean_artist']}**")
    
    embed.add_field(name="🎵 검색 결과", value="\n".join(results), inline=False)
    
    if len(matching_songs) > 10:
        embed.add_field(name="📋 안내", value=f"더 많은 결과가 있습니다. ({len(matching_songs) - 10}곡 추가)", inline=False)
    
    embed.set_footer(text="💡 곡 제목을 클릭하면 YouTube에서 바로 들을 수 있어요!")
    await ctx.send(embed=embed)

@bot.command(name='랜덤')
async def random_songs(ctx, count: int = 5):
    """랜덤으로 몇 곡 추천"""
    count = max(1, min(count, 10))  # 1~10 범위로 제한
        
    songs = music_bot.get_playlist_songs()
    if not songs:
        await ctx.send("❌ 재생목록을 불러올 수 없습니다.")
        return
    
    # 랜덤 곡 선택
    random_songs_list = random.sample(songs, min(count, len(songs)))
    
    embed = discord.Embed(
        title=f"🎲 랜덤 추천 {count}곡",
        description="오늘 이 곡들은 어떠세요?",
        color=0xFF6B6B
    )
    
    song_list = []
    for i, song in enumerate(random_songs_list, 1):
        clean_artist = music_bot.clean_artist_name(song['artist'])
        
        title = song['title']
        if len(title) > 35:
            title = title[:32] + "..."
        
        song_list.append(f"`{i}.` [{title}]({song['url']}) - **{clean_artist}**")
    
    embed.add_field(name="🎵 추천 곡들", value="\n".join(song_list), inline=False)
    embed.set_footer(text="💡 곡 제목을 클릭하면 YouTube에서 바로 들을 수 있어요!")
    
    await ctx.send(embed=embed)

@bot.command(name='히스토리')
async def song_history(ctx):
    """최근에 플레이한 곡 히스토리"""
    if music_bot.songs_history:
        embed = discord.Embed(
            title="📜 최근 재생된 곡들",
            description="\n".join([f"{i+1}. {song}" for i, song in enumerate(music_bot.songs_history[-10:])]),
            color=0x95E1D3
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("🎵 아직 재생된 곡이 없습니다.")

@bot.command(name='도움말')
async def help_command(ctx):
    """봇 사용법 안내"""
    embed = discord.Embed(
        title="🎵 음악 봇 사용법",
        description="YouTube 재생목록과 연동된 음악 봇입니다!",
        color=0x9B59B6
    )
    
    commands_list = [
        "`!오늘의곡` - 오늘의 랜덤 곡 추천",
        "`!재생목록 [페이지]` - 전체 재생목록 보기",
        "`!검색 <곡명/가수명>` - 재생목록에서 곡 검색",  
        "`!랜덤 [개수]` - 랜덤으로 몇 곡 추천 (기본 5곡)",
        "`!히스토리` - 최근 재생된 곡들",
        "`!도움말` - 이 메시지 보기"
    ]
    
    embed.add_field(name="📋 명령어 목록", value="\n".join(commands_list), inline=False)
    embed.add_field(name="💡 팁", value="• 곡 제목을 클릭하면 YouTube에서 바로 재생됩니다!\n• 봇 닉네임에서 현재 추천곡을 확인할 수 있어요", inline=False)
    embed.set_footer(text="매일 자동으로 새로운 곡이 추천됩니다! 🎶")
    
    await ctx.send(embed=embed)

@bot.command(name='테스트')
async def test_command(ctx):
    """봇 연결 테스트"""
    await ctx.send("🤖 봇이 정상적으로 작동 중입니다!")

@tasks.loop(hours=24)
async def daily_song_task():
    """매일 정해진 시간에 새로운 곡 전송"""
    now = datetime.now()
    if now.hour == 9 and now.minute == 0:
        print("⏰ 일일 음악 업데이트 시간입니다!")
        await music_bot.send_daily_song()

@daily_song_task.before_loop
async def before_daily_song():
    await bot.wait_until_ready()

def check_environment():
    """환경변수가 제대로 설정되었는지 확인"""
    missing = []
    
    if not DISCORD_TOKEN:
        missing.append("DISCORD_TOKEN")
    if not YOUTUBE_API_KEY:
        missing.append("YOUTUBE_API_KEY")
    if not PLAYLIST_ID:
        missing.append("PLAYLIST_ID")
    if not CHANNEL_ID:
        missing.append("CHANNEL_ID")
    if not GUILD_ID:
        missing.append("GUILD_ID")
    
    if missing:
        print(f"❌ 다음 환경변수가 누락되었습니다: {', '.join(missing)}")
        print("✅ .env 파일을 확인해주세요.")
        return False
    
    print("✅ 모든 환경변수가 설정되었습니다.")
    return True

# 봇 실행
if __name__ == "__main__":
    if check_environment():
        try:
            print("🚀 Discord 음악 봇을 시작합니다...")
            bot.run(DISCORD_TOKEN)
        except discord.LoginFailure:
            print("❌ Discord 로그인 실패! 토큰을 확인해주세요.")
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ 환경변수 설정을 완료한 후 다시 실행해주세요.")
