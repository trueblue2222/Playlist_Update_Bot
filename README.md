# Playlist_Update_Bot
96% Claude AI의 도움을 받아 만든 내 유튜브 계정 플레이리스트를 연동하여 디코에서 들을 수 있는 디스코드봇 (로컬용)
https://discord.com/oauth2/authorize?client_id=1400714065642389524&permissions=3213312&integration_type=0&scope=bot

파일 구조 :
```
discord-music-bot
├── bot.py          // 실제 디코봇 기능 구현된 소스파일
├── test_bot.py     // 토큰 로드 & 연동 확인용 테스트 소스파일
├── .env            // 디코 토큰, 유튜브 계정 API, 플리 ID, 디스코드 서버 ID, 채널 ID 저장 .env 파일
└── requirements.txt // 라이브러리 버전 명시 txt 파일
```

사용 방법 (로컬용) :

0. 자신의 디코 계정에서 디코봇을 하나 아무거나 만든다. 권한 설정을 적당히 해준다. 그리고 디코봇을 넣어둘 디코 서버도 하나 만들어준다.

1. (중요) .env 파일에 토큰 정보를 정확하게 입력한다. 차례대로 디코봇 토큰, 유튜브 계정 api key, 플리 id, 디코봇이 있는 서버 id, 채널 id이다.
참고로 디코봇 토큰은 https://discord.com/developers/applications 에서 reset token을 누르면 토큰 복사가 가능하다. 민감한 정보이므로 조심히 사용하자.
유튜브 계정 api key는 구글 클라우드 라이브러리에서 'Youtube Data API v3'를 이용하면 발급받을 수 있다. 이 역시 민감한 정보이므로 조심히 사용하자.
플리 id는 내가 원하는 플리의 url에 'list=' 뒤에 있는 정보이다.
디코봇이 있는 서버 id, 채널 id는 디코 설정에서 개발자 모드를 킨 다음 각각 우클릭하면 볼 수 있다.
.env 파일 내의 소스코드는 다음과 같이 작성하면 된다.
```
DISCORD_TOKEN=여기에디스코드봇토큰입력
YOUTUBE_API_KEY=여기에유튜브계정API키입력
PLAYLIST_ID=여기에재생목록ID입력
CHANNEL_ID=여기에디스코드서버내채널ID입력
GUILD_ID=여기에디스코드서버ID입력
```

3. test_bot.py 터미널에서 토큰이 잘 로드되는지, 연동이 잘 되는지, 서버에 연결되는지 확인해본다. 명령어 python test_bot.py로 테스트 가능하다.
오류가 나면 디코봇 API 권한 설정이 추가로 필요하거나 연동된 유튜브 플레이리스트가 비공개인 등등의 문제일 것이다.

<img width="1787" height="444" alt="image" src="https://github.com/user-attachments/assets/67b94c8f-6605-4f02-a2ac-de21a2cbffa2" />


3. test_bot.py에서 문제가 없으면 bot.py 터미널로 들어가 디코봇을 실행시켜준다. 명령어 python bot.py로 실행 가능하다.

<img width="1744" height="344" alt="image" src="https://github.com/user-attachments/assets/81316d4b-3253-436a-afbb-f57437d01cbc" />

4. 디코봇을 넣어둔 디코 서버로 가서 이것저것 해본다. 주요 명령어는 다음 사진을 참고하자. (8/4 수정 : 연동된 유튜브 재생목록 바로가기 링크 기능 추가)

<img width="1074" height="768" alt="image" src="https://github.com/user-attachments/assets/d68d6259-c14e-4c02-a416-428c31889d7e" />

<img width="1086" height="618" alt="image" src="https://github.com/user-attachments/assets/8861f497-00ff-4c0b-aa73-aae75a89cbfb" />
<img width="832" height="498" alt="image" src="https://github.com/user-attachments/assets/7f1ebcdb-7448-494f-bdf4-68b799a54663" />








원래는 내 디스코드 프로필을 내 유튜브 계정의 플레이리스트와 연동하여 그 중 노래 하나를 하루마다 자동으로 선택해서 '내 소개' 란에 하나 적어두는 디코봇을 만들고 싶었다. 근데 이런 디코봇은 사용자 계정처럼 행동하는 '셀프봇'이라고 한다. 디코봇이 실제 사용하고 있는 사용자의 계정에 접근하는 것은 Discord 이용약관에 위반된다고 한다. 이런 디코봇을 만들면 계정이 정지된다고 한다. 아쉽지만 내가 원래 계획한 기능을 지금 당장 만드는 것은 어려울 것 같다고 생각하여 그냥 유튜브 계정 연동 및 디코 내에서 음악을 틀어줄 수 있는 디코봇을 만들어보았다. 물론 내가 코드를 하나하나 짠 건 아니고 Claude AI와의 긴밀한 협업을 통해 만든 것이다..


   
