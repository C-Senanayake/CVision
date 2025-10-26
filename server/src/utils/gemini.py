import os
import json
from google import genai
from dotenv import load_dotenv
load_dotenv()

class GeminiPDFExtractor:
    def __init__(self):
          self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    async def extract_and_structure_pdf(self, pdf_file_name:str) -> dict:
          """Extract and structure PDF content into JSON"""

          base_dir = os.path.dirname(os.path.abspath(__file__)) 
          file_path = os.path.join(base_dir, f"../data/{pdf_file_name}")
      #     print("Resolved path:", file_path)
      #     print("Exists:", os.path.exists(file_path))
          # Upload PDF to Gemini
          pdf_file = self.client.files.upload(file=file_path)

          prompt = """
          Analyze this PDF CV/Resume and extract structured data in JSON format.

          Return a JSON object with this exact structure:
          {
              "personal_info": {
                    "name": "Full name",
                    "email": "email address",
                    "phone": "phone number",
                    "address": "address",
                    "linkedin": "LinkedIn URL", //If can extract the URL, extract it
                    "website": "personal website", //If can extract the URL, extract it
                    "github": "Github URL", //If can extract the URL, extract it
                    "medium": "Medium URL" //If can extract the URL, extract it
              },
              "professional_summary": "Summary text",
              "work_experience": [
                    {
                        "company": "Company name",
                        "position": "Job title",
                        "start_date": "Start date",
                        "end_date": "End date or 'Present'",
                        "description": "Job description",
                        "achievements": ["Achievement 1", "Achievement 2"]
                    }
              ],
              "education": [
                    {
                        "institution": "University name",
                        "degree": "Degree type",
                        "field": "Field of study",
                        "graduation_year": "Year",
                        "gpa": "GPA if available",
                        "class": "Class achieved"
                    },
                    {
                        "institution": "School/College",
                        "results": "A/L results",
                        "year": "Year"
                    }
              ],
              "skills": {
                    "technical_skills": ["Skill 1", "Skill 2"],
                    "soft_skills": ["Skill 1", "Skill 2"],
                    "languages": ["Language 1", "Language 2"]
              },
              "certifications": ["Cert 1", "Cert 2"],
              "projects": [
                    {
                        "name": "Project name",
                        "description": "Project description",
                        "technologies": ["Tech 1", "Tech 2"],
                        "repository": "Repository URL", //If the correct url for the repository given, extract it
                        "url": "Live URL"
                    }
              ],
              "researchs and publications": [
                    {
                         "name": "Research/publication name",
                         "duration": "Duration",
                         "key_areas": "Key Areas",
                         "Achievements": "Achievements,
                         "Links": "Attached link with description"
                    }
              ],
              "interest": "["Interests 1", "Interests 2"]",
              "volunteer": "["Volunteering 1", "Volunteering 2"]",
              "achievements": ["Achievement 1", "Achievement 2"]
              "references": [{
                    "name": "Name",
                    "position": "Position",
                    "email": "Email address",
                    "phone_number": "Mobile Number",
              }]
          }

          Extract only information that is explicitly present in the CV. Use empty strings or arrays for missing information.
          """
        
          response = self.client.models.generate_content(
               model="gemini-2.0-flash",
               contents=[prompt, pdf_file]
          )
      #     print("TEXT:::",response.text)
          # Clean up the response to extract JSON
          response_text = response.text.strip()

          # Find JSON in the response
          json_start = response_text.find('{')
          json_end = response_text.rfind('}') + 1

          if json_start != -1 and json_end != -1:
              json_text = response_text[json_start:json_end]
            #   print("JSON::",json_text)
              return json.loads(json_text)
          else:
              raise ValueError("Could not extract valid JSON from response")
