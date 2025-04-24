import { useState, useEffect, useRef } from 'react';

const SPEECH_TIMEOUT = 2000; // 2초 침묵 후 인식 일시 중지

interface SpeechToTextProps {
  onTranscript: (text: string) => void;
}

export function SpeechToText({ onTranscript }: SpeechToTextProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState('');

  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const timeoutIdRef = useRef<NodeJS.Timeout | null>(null);

  const isSpeechRecognitionSupported =
    'SpeechRecognition' in window || 'webkitSpeechRecognition' in window;

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if (timeoutIdRef.current) {
        clearTimeout(timeoutIdRef.current);
      }
    };
  }, []);

  const startRecording = () => {
    try {
      setIsRecording(true);
      setTranscript(''); // 새 녹음 시작 시 기존 텍스트 초기화

      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();

      // 설정 최적화
      recognitionRef.current.lang = 'ko-KR';
      recognitionRef.current.continuous = true; // 연속 인식 활성화
      recognitionRef.current.interimResults = true;
      recognitionRef.current.maxAlternatives = 3; // 여러 대체 결과 제공

      // 이벤트 핸들러
      recognitionRef.current.onresult = (event) => {
        // 이전 타임아웃 초기화
        if (timeoutIdRef.current) {
          clearTimeout(timeoutIdRef.current);
        }

        const currentTranscript = Array.from(event.results)
          .map(result => result[0].transcript)
          .join('');

        setTranscript(currentTranscript);

        // 중간 결과가 아닌 경우에만 텍스트 전달
        if (event.results[0].isFinal) {
          onTranscript(currentTranscript);
        }

        // 음성 감지 후 일정 시간 대기 타이머 설정
        timeoutIdRef.current = setTimeout(() => {
          if (recognitionRef.current) {
            try {
              // 인식 종료 후 잠시 대기하다가 다시 시작
              recognitionRef.current.stop();
            } catch (e) {
              console.error("Error stopping recognition:", e);
            }
          }
        }, SPEECH_TIMEOUT); // 2초 침묵 후 인식 일시 중지
      };

      recognitionRef.current.onend = () => {
        // 인식이 종료되었을 때 자동으로 다시 시작 (중지 버튼 누르지 않은 경우에만)
        if (isRecording && !isProcessing) {
          try {
            recognitionRef.current?.start();
          } catch (e) {
            console.error("Error restarting recognition:", e);
          }
        } else {
          setIsRecording(false);
          setIsProcessing(false);
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);

        // 'no-speech' 에러는 무시하고 다시 시작
        if (event.error === 'no-speech') {
          try {
            setTimeout(() => {
              if (isRecording && recognitionRef.current) {
                recognitionRef.current.start();
              }
            }, 100);
          } catch (e) {
            console.error("Error restarting after no-speech:", e);
          }
        } else if (event.error === 'network') {
          // 네트워크 에러 시 재연결 시도
          setTimeout(() => {
            if (isRecording) {
              startRecording();
            }
          }, 1000);
        } else {
          setIsRecording(false);
          setIsProcessing(false);
        }
      };

      // 인식 시작
      recognitionRef.current.start();
    } catch (error) {
      console.error('Failed to start speech recognition:', error);
      setIsRecording(false);
    }
  };

  const stopRecording = () => {
    setIsProcessing(true);

    // 타임아웃 정리
    if (timeoutIdRef.current) {
      clearTimeout(timeoutIdRef.current);
      timeoutIdRef.current = null;
    }

    // 최종 텍스트가 있으면 전달
    if (transcript && transcript.trim() !== '') {
      onTranscript(transcript);
    }

    // 인식 중지
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

  if (!isSpeechRecognitionSupported) {
    return (
      <div className="speech-to-text">
        <button disabled title="브라우저가 음성 인식을 지원하지 않습니다">
          음성 입력 불가
        </button>
      </div>
    );
  }

  return (
    <div className="speech-to-text">
      <button
        onClick={isRecording ? stopRecording : startRecording}
        disabled={isProcessing}
        className={isRecording ? 'recording' : ''}
        aria-label={isRecording ? '녹음 중지' : '음성 입력'}
      >
        {isRecording ? '녹음 중지' : isProcessing ? '처리 중...' : '음성 입력'}
      </button>
      {isRecording && <span className="recording-indicator">🔴</span>}
    </div>
  );
}