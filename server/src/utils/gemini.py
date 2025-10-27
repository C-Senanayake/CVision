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
    
    async def generate_marks(self, resumeContent: dict, jobData: dict) -> dict:
        job_name = jobData.get("jobName")
        if jobData.get("division") == 'se':
            division = "Software Engineering"
        if jobData.get("division") == 'qe':
            division = "Test Automation Engineering"
        if jobData.get("division") == 'devops':
            division = "DevOps Engineering"
        job_description = jobData.get("jobDescription")
        criteria_object = jobData.get("criteria")
        resume_content = resumeContent
        guidance_section = {
            "A/L or Advanced Level Results": "This mainly has 3 subjects which are considered as the main subjects. Best result for a subject is 'A', next 'B', 'C', 'S' and the lowest is 'F'. Consider district and island ranks also. (having an island rank above 300 or a district rank above 100 can be considered as a good result",
            "GPA or CGPA": "This is a cumulative measure of a student's academic performance, typically on a scale of 4.0. So the best is 4.0, 3.9-3.7 is good, 3.5-3.0 is average and lower than 2.0 is really poor.",
            "Projects": "List of projects undertaken, with a focus on those relevant to the job description.",
            "Work Experience": "Details of previous employment, including roles, responsibilities, and achievements.",
            "Skills": "Technical and soft skills relevant to the job description.",
            "Certifications": "Relevant certifications that enhance the candidate's qualifications for the job."
        }
        prompt_template = f"""
            You are an expert technical recruiter evaluating resumes for the position of **{job_name}** in the **{division}** division.

            You are given:
            1. A **job description**.
            2. A candidate’s **resume content**.
            3. A **criteria object** containing evaluation categories and their maximum marks.
            4. A **guidance section** describing what is considered strong or weak performance for each criterion.

            ### Your task:
            Compare the resume content against the job description and assign marks for each criterion based on how well the resume matches the expectations for this job and division.

            ### Rules:
            - Each criterion in the given object has a *maximum mark* (e.g., 10, 20, etc.).
            - Give a *mark between 0 and the maximum* for each.
            - Give a **mark fraction** for each and save the mark_fraction in the object as **mark/maximum mark in criteria**.
            - Provide a *one-sentence explanation* for each mark explaining why that score was given.
            - **Do NOT** give marks for `GitHub` or `LinkedIn` (skip them entirely) but add these 2 to your generated obeject with mark 0/maximum mark in criteria and give description as not generating mark for these.
            - Be consistent and fair in marking.
            - Use the “guidance section” to understand what good or poor performance looks like for each criterion.

            ### Example Output Format:
            Return your answer as a JSON object like this:
            {{
              "A/L": {{
                "mark": 8,
                "mark_fraction": "8/10"
                "explanation": "Strong academic results relevant to the role."
              }},
              "GPA": {{
                "mark": 9,
                "mark_fraction": "9/20"
                "explanation": "Excellent GPA showing strong technical knowledge."
              }},
              ...
            }}

            ### Input Data

            **Job Name:** {job_name}  
            **Division:** {division}  

            **Job Description:**
            {job_description}

            **Resume Content:**
            {resume_content}

            **Evaluation Criteria (Max Marks):**
            {criteria_object}

            **Guidance Section (Best vs. Worst Examples):**
            {guidance_section}

            Evaluate the resume based on the items specified in the criteria_object. Use only the information provided in the guidance_section for your evaluation. 
            Return the results strictly in JSON format, including each criterion with its assigned mark and a brief explanation.
            """
        # print("PROMPT::", prompt_template)
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_template
        )
        # Clean up the response to extract JSON
        response_text = response.text.strip()
        # Find JSON in the response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start != -1 and json_end != -1:
            json_text = response_text[json_start:json_end]
            return json.loads(json_text)
        else:
            raise ValueError("Could not extract valid JSON from response")
