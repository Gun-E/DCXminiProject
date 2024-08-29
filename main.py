# main.py
from fastapi import FastAPI, Query, HTTPException
from typing import List
from pydantic import BaseModel
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import logging

app = FastAPI()

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id='b7b2ec17e994405894bd50c4c681b1a1',
    client_secret='6d135d223d74493e89e3a55795c64fea'))
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# FastAPI 앱 실행
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="192.168.219.68",
        port=8000,
        reload=True
    )


@app.get("/")
async def read_root():
    return {"testWord": "파이썬 통신 성공"}


# 요청 DTO 정의
class SongTitleDto(BaseModel):
    title: str


# 응답 DTO 정의
class SongTitle(BaseModel):
    title: str
    artist: str
    url: str

@app.post("/spotify", response_model=List[SongTitle])
async def search_song_titles(request: SongTitleDto):
    logger.info(f"title: {request.title}")
    received_title = request.title
    try:
        results = sp.search(q=received_title, type='track', limit=10)
        song_titles = [
            SongTitle(
                title=track['name'],
                artist=", ".join([artist['name'] for artist in track['artists']]),
                url=track['external_urls']['spotify']
            ) for track in results['tracks']['items']
        ]
        return song_titles
    except spotipy.exceptions.SpotifyException as e:
        raise HTTPException(status_code=404, detail=f"Spotify에서 해당 노래를 찾을 수 없습니다: {e}")
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="서버 오류가 발생했습니다.")
