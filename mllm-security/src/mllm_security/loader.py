import json

DEFAULT_VIDEO_CAPTION_PATH = (
    "../vision-assistant-for-driving/instruct-data/HAD/HAD-captions.json"
)
DEFAULT_INSTRUCTION_PATH = (
    "../vision-assistant-for-driving/data/HAD_train_data/HAD-Instruct.json"
)

with open(DEFAULT_VIDEO_CAPTION_PATH, "r") as f:
    video_captions_raw = json.load(f)

video_captions = {}
for video_caption in video_captions_raw:
    video_captions[video_caption["video_id"]] = video_caption["desc"]
print("Loaded", len(video_captions), "video captions")

with open(DEFAULT_INSTRUCTION_PATH, "r") as f:
    instructions = json.load(f)
    print("Loaded", len(instructions), "instructions")

ANSWERING_PROMPT = """
-----------------------------------
As an AI visual assistant of a driver, you are watching front-view road for around 20 seconds. You are given the summarization of road events and manuever of your ego-car during 20 seconds and some detailed information, which inlcudes "[attention]" you may take care of while driving, "[cause]" that makes you do [sitmulus-driven] behavior, "[goal-oriented]" that you do with a purpose of going somewhere or else, "[stimulus-driven]" behavior that reaction to some changes on road or traffic, "[Steering angles]" that is steering angle of ego-car at every second, and "[Velocities]" that is velocity of ego-car at every second.

The types of questions can be categorized into three types: Conversation, Description, and Reasoning.
For Conversation, you can respond according to the given situation without any specific format constraints.
When you answer description type questions, create a detailed description based on given information of current driving scene. Say everything you see, but do not inlcude what you did not see. The description should be less than 150 words.
When answer the reasoning question, create a situational reasoning answer between yourself and someone inquiring about the current driving scene. Make sure the response reflect the tone of a AI visual assistant of a driver, actively observing the driving situations and answering questions. The answer should be regarding situational Reasoning for traffic understanding.

When you answer the question, never mention given description directly, such as veclocity and steering angle. If a question cannot be answered based on the given descriptions, respond with "It does not present such information" rather than indicating that the information comes from text descriptions.

Never give time information included in the description.

Answer the following question as if real people were talking!

Note, indicate your car as ego-car.

Question:
"""

if __name__ == "__main__":    
    for instruction in instructions:
        caption = video_captions[instruction["video_id"]]
        qa = instruction["QA"]
        question = qa["q"]
        expected_answer = qa["a"]

        query = caption + ANSWERING_PROMPT + question

        print(query)
        print("-" * 35)
        print("Answer:", expected_answer)
        break
