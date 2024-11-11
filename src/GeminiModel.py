import re
from google.generativeai import GenerativeModel
from fastapi import HTTPException
import google.generativeai as genai
import os
from dotenv import load_dotenv
import PIL
from PIL import Image
from .utils import download_file
from pillow_heif import register_heif_opener
import numpy as np
import time
import json
import asyncio
from .models import ImageDescriptions
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
    async def process_image_parts_from_social_media(self, all_images):
        ans = []
        for i in all_images:
            if i.get("content_urls"):
                contents = i.get("content_urls")
                for url in contents:
                    content_url = {"data": url,"social_media":i['social_media'], "timestamp":i['timestamp'], "location":i['location'], "type":i['type']  }
                    ans.append(content_url)
        print(len(ans))
        for i in ans:
            print(i)
            print("")
        return ans
    def process_response_text(self, response_text, ):
        
        pass
    def format_prompt(self, prompt):
        to_append = """\n Use this JSON schema:
        Description: str
        Return: list[Description] 
        """
        return prompt  + to_append

    async def get_gemini_response_image(self, input_text: str, image_parts_list: list) -> str:
        # input_text = self.format_prompt(input_text)
        self.model = GenerativeModel(os.getenv('GEMINI_IMAGE_MODEL_NAME'))
        images = []
        image_parts_list = await self.process_image_parts_from_social_media(image_parts_list)
        for image_part in image_parts_list:
            if image_part['type'].lower() == "photo":
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
            responses = []
            for image in images:
                response = self.model.generate_content([input_text] + images, generation_config=genai.GenerationConfig(
        response_mime_type="application/json", response_schema=ImageDescriptions
    ))
                responses.append(response.text)
            #print("Response Revieved", response) 
            return responses
        except Exception as e:
            # current_app.logger.error(f"Error fetching Gemini response: {e}")
            #print(f"Error fetching Gemini response: {e}")
            raise HTTPException(status_code=500, detail=f"Error fetching Gemini response: {str(e)}")
        
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
    prompt = "You are an expert in delivering quality image captions for the given images,you describe details of of what the person in the image is doing and try to describe his personality traits, interest areas and experiences in a story form. limit your response to a single line per image and separate image stories with a single new line character"

    prompt_2 = "You are an expert in understanding human behavoir, A person has posted the following images on different social media handles, write a one liner sentence of what do you understand from the given image including the facts like his personality  traits, interest areas and experiences in a story form limit your response to a single line per image and separate image stories with a single new line character.strictly Do not rank images calling them first image, second image, final image etc. Just return the image intepretations in one liner do not summarize them at last"

    prompt_3 = """Craft a compelling narrative around the individual's personality, interests, and experiences based on the images shared on various social media platforms. Uncover layers of their character traits, passions, and life journey from the visual storytelling presented. Remember to intrigue and engage with concise, impactful observations. strictly follow the following  in the backticks for all the images
    ```
    image 1: image_one_story \n
    ```


    
    """
    with open("output.json", "r") as f:
        data = json.loads(f.read())
    output = asyncio.run(gem.get_gemini_response_image(prompt_3, data))
    print(output)

