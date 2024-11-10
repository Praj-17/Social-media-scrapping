import re
from google.generativeai import GenerativeModel
from fastapi import HTTPException
import google.generativeai as genai
import os
from dotenv import load_dotenv
import PIL
from PIL import Image
from utils import download_file
from pillow_heif import register_heif_opener
import numpy as np
import time
import json
import asyncio
load_dotenv()

register_heif_opener()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class GeminiRunnerClass:
    def __init__(self) -> None:
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            self.model = GenerativeModel(os.getenv('GEMINI_MODEL_NAME'))
    def extract_persona_from_response(self, response_text: str, user_id: str) -> dict:
        """Extract persona details from the Gemini response text."""
        try:
            interests_match = re.search(r'Interests:\s*(.+)', response_text)
            personality_traits_match = re.search(r'Personality Traits:\s*(.+)', response_text)
            hobbies_match = re.search(r'Hobbies:\s*(.+)', response_text)
            skills_match = re.search(r'Skills:\s*(.+)', response_text)
            values_match = re.search(r'Values:\s*(.+)', response_text)
            emotions_match = re.search(r'Emotions:\s*(.+)', response_text)
            age_group_match = re.search(r'Age Group:\s*(.+)', response_text)
            gender_match = re.search(r'Gender:\s*(.+)', response_text)
            experiences_match = re.search(r"Experiences:\s*(.+)", response_text)
            transcribed_match = re.search(r"Transcribed Text:\s*(.+)", response_text)
            confidence = re.search(r"Confidence:\s*(.+)", response_text)

            persona = {
                "user_id": user_id,
                "interests": (interests_match.group(1)).split(",") if interests_match else None,
                "personality_traits": (personality_traits_match.group(1)).split(",") if personality_traits_match else None,
                "hobbies": (hobbies_match.group(1)).split(",") if hobbies_match else None,
                "skills": (skills_match.group(1)).split(",") if skills_match else None,
                "values": (values_match.group(1)).split(",") if values_match else None,
                "emotions": (emotions_match.group(1)).split(",") if emotions_match else None,
                "age_group": age_group_match.group(1) if age_group_match else None,
                "gender": gender_match.group(1) if gender_match else None,
                "experiences": (experiences_match.group(1)).split(",") if experiences_match else None,
                "transcribed_text": transcribed_match.group(1) if transcribed_match else None,
                "confidence": int((confidence.group(1)).strip()) if confidence else 0
            }
            return persona
        except Exception as e:
            # current_app.logger.error(f"Error extracting persona: {e}")
            raise HTTPException(status_code=500, detail="Error extracting persona")

    async def wait_for_file_active(self, file_uri: str):
        """Wait until the uploaded file becomes ACTIVE."""
        while True:
            file_info = genai.get_file("shityy")
            print({"file_info": file_info})
            if file_info.state.name == "ACTIVE":
                break
            elif file_info.state.name == "FAILED":
                genai.delete_file(name="shityy")
                raise HTTPException(status_code=500, detail="File processing failed")
            time.sleep(10)

    async def upload_and_verify_file(self, file_path: str):
        print(f"Uploading file...")
        uploaded_file = genai.upload_file(path=file_path, name="shityy")
        print(f"Completed upload: {uploaded_file.uri}")
        await self.wait_for_file_active(uploaded_file.uri)

        return uploaded_file


    async def get_gemini_response(self, input_text: str, image_parts: list) -> str:
        self.model = GenerativeModel(os.getenv('GEMINI_MODEL_NAME'))
        try:
            response = self.model.generate_content([input_text, *image_parts])
            return response.text
        except Exception as e:
            # current_app.logger.error(f"Error fetching Gemini response: {e}")
            print(f"Error fetching Gemini response: {e}")
            raise HTTPException(status_code=500, detail="Error fetching Gemini response")
    async def process_image_parts_from_social_media(self, contents):
        ans = []
        for i in contents:
            if i.get("type"):
                type = i.get("type")
                if type.lower() == "photo":
                    if i.get("content_urls"):
                        contents = i.get("content_urls")
                        for i in contents:
                            content_url = {"data": i}
                            ans.append(content_url)
        return ans

    async def get_gemini_response_image(self, input_text: str, image_parts_list: list) -> str:
        self.model = GenerativeModel(os.getenv('GEMINI_IMAGE_MODEL_NAME'))
        images = []
        image_parts_list = await gem.process_image_parts_from_social_media(image_parts_list)
        for image_part in image_parts_list:
            file_path = download_file(image_part['data'])
            img = Image.open(file_path)
            img_arr = np.array(img)
            image_array = img_arr.astype(np.uint8)  # Ensure array is in uint8 format
            # Convert the NumPy array back to a PIL Image
            image = Image.fromarray(image_array)
            images.append(image)
            img.close()
            os.remove(file_path)


        try:
            response = self.model.generate_content([input_text] + images)
            #print("Response Revieved", response) 
            return response.text
        except Exception as e:
            # current_app.logger.error(f"Error fetching Gemini response: {e}")
            #print(f"Error fetching Gemini response: {e}")
            raise HTTPException(status_code=500, detail="Error fetching Gemini response")
        
    async def get_gemini_response_audio(self, input_prompt, audio_data: list) -> str:
        audio_data = audio_data[0]
        file_path = download_file(audio_data['data'], filename="tempaudio.mp3")
        self.model = GenerativeModel(os.getenv('GEMINI_MODEL_NAME'))
        audio_answer  = await self.upload_and_verify_file(file_path)
        try:
            response = self.model.generate_content([input_prompt, audio_answer])
            #print("Response Revieved", response)
            os.remove(file_path)
            genai.delete_file(name="shityy")
            return response.text
        except Exception as e:
            # current_app.logger.error(f"Error fetching Gemini response: {e}")
            genai.delete_file(name="shityy")
            #print(f"Error fetching Gemini response: {e}")
            raise HTTPException(status_code=500, detail="Error fetching Gemini response")
if __name__ =="__main__":
    gem = GeminiRunnerClass()
    prompt = "You are an expert in delivering quality image captions for the given images,you describe details of of what the person in the image is doing and try to describe his personality traits , interest areas and experiences in a story "
    with open("output.json", "r") as f:
        data = json.loads(f.read())
    output = asyncio.run(gem.get_gemini_response_image(prompt, data))
    print(output)

