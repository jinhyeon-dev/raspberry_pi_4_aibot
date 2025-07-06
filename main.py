import os
import speech_recognition as sr
from gtts import gTTS
import pygame
import openai
from dotenv import load_dotenv
import time
import tempfile

# 환경 변수 로드
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv('OPEN_AI_KEY')

# 음성 인식기 초기화
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# pygame mixer 초기화 (음성 재생용)
pygame.mixer.init()

def listen_to_voice():
    """마이크로부터 음성 입력 받기"""
    with microphone as source:
        print("듣고 있습니다... 말씀해 주세요.")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            # 음성 입력 대기 (타임아웃 5초, 구문 완료 대기 2초)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("음성 인식 중...")
            
            # Google 음성 인식 사용
            text = recognizer.recognize_google(audio, language='ko-KR')
            print(f"인식된 텍스트: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("음성 입력 시간이 초과되었습니다.")
            return None
        except sr.UnknownValueError:
            print("음성을 인식할 수 없습니다.")
            return None
        except sr.RequestError as e:
            print(f"음성 인식 서비스 오류: {e}")
            return None

def get_ai_response(prompt):
    """OpenAI API를 통해 응답 받기"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "당신은 친절하고 도움이 되는 AI 어시스턴트입니다. 간결하고 명확하게 한국어로 답변해 주세요. 짧고 간단하게 문장으로 답변해주세요."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"OpenAI API 오류: {e}")
        return "죄송합니다. 응답을 생성하는 중 오류가 발생했습니다."

def speak_text(text):
    """텍스트를 음성으로 변환하여 출력"""
    try:
        # gTTS로 텍스트를 음성으로 변환
        tts = gTTS(text=text, lang='ko', slow=False)
        
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            
            # pygame으로 재생
            pygame.mixer.music.load(tmp_file.name)
            pygame.mixer.music.play()
            
            # 재생이 끝날 때까지 대기
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            # 임시 파일 삭제
            os.unlink(tmp_file.name)
            
    except Exception as e:
        print(f"음성 출력 오류: {e}")

def main():
    print("AI 음성 비서를 시작합니다.")
    print("종료하려면 '종료', '그만', '끝'이라고 말해주세요.\n")
    
    speak_text("안녕하세요. AI 음성 비서입니다. 무엇을 도와드릴까요?")
    
    while True:
        # 음성 입력 받기
        user_input = listen_to_voice()
        
        if user_input is None:
            speak_text("다시 한 번 말씀해 주세요.")
            continue
        
        # 종료 명령 확인
        if user_input in ['종료', '그만', '끝', '멈춰']:
            speak_text("감사합니다. 안녕히 계세요.")
            print("프로그램을 종료합니다.")
            break
        
        # AI 응답 받기
        print("AI 응답을 기다리는 중...")
        ai_response = get_ai_response(user_input)
        print(f"AI 응답: {ai_response}")
        
        # 응답을 음성으로 출력
        speak_text(ai_response)
        
        # 다음 입력 전 잠시 대기
        time.sleep(0.5)

if __name__ == "__main__":
    main()