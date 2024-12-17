# Poisoning_v1의 출력 설명

모든 Steering Angle, Velocity, Visual 세 모달리티에 대해 각각 또는 두 개 이상 조합의 데이터를 오염시키고 공격

## 개선해야 할 점

- Confidence(=logprob)데이터가 없으므로 다시 테스트 필요
- openai.Completion.create 호출 시 logprobs=1로 설정해서 확률을 출력하게 설정
- 추후 활용을 위해 OpenAI API의 모든 Response를 저장
- temperature=0으로 설정하기 (일관된 답변을 얻기 위해)