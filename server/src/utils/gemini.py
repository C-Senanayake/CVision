import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

class GeminiPDFExtractor:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    async def extract_and_structure_pdf(self, pdf_file_name:str) -> dict:
          """Extract and structure PDF content into JSON"""

          base_dir = os.path.dirname(os.path.abspath(__file__)) 
          file_path = os.path.join(base_dir, f"../data/{pdf_file_name}")
      #     print("Resolved path:", file_path)
      #     print("Exists:", os.path.exists(file_path))
          # Upload PDF to Gemini
          pdf_file = genai.upload_file(file_path)

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
        
          model = genai.GenerativeModel("gemini-2.0-flash")
          response = model.generate_content([prompt, pdf_file])
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
    
    async def generate_marks(self, resumeContent: dict, jobData: dict, githubData: dict = None) -> dict:
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
        
        # Prepare GitHub data summary if available
        github_summary = "No GitHub data available."
        if githubData and githubData.get("fetch_status") == "success":
            profile = githubData.get("profile", {})
            stats = githubData.get("statistics", {})
            repo_stats = stats.get("repositories", {}) if stats else {}
            lang_stats = stats.get("languages", {}) if stats else {}
            activity_stats = stats.get("activity", {}) if stats else {}
            
            github_summary = f"""
GitHub Profile Analysis:
- Username: {profile.get('username', 'N/A')}
- Account Age: {stats.get('account_age_years', 0)} years
- Total Public Repositories: {repo_stats.get('total_repositories', 0)}
- Original Repositories (not forks): {repo_stats.get('total_original_repos', 0)}
- Total Stars Received: {repo_stats.get('total_stars', 0)}
- Total Forks: {repo_stats.get('total_repository_forks', 0)}
- Followers: {profile.get('followers', 0)}
- Primary Programming Language: {lang_stats.get('primary_language', 'N/A')}
- Total Languages Used: {lang_stats.get('total_languages', 0)}
- Recent Activity: {'Active in last 30 days' if activity_stats.get('is_active') else 'Inactive'}
- Top Repositories: {', '.join([f"{repo['name']} ({repo['stars']} stars)" for repo in repo_stats.get('top_repositories', [])[:3]])}
- Location: {profile.get('location', 'N/A')}
- Bio: {profile.get('bio', 'N/A')}
"""
        
        guidance_section = {
            "A/L or Advanced Level Results": "This mainly has 3 subjects which are considered as the main subjects. Best result for a subject is 'A', next 'B', 'C', 'S' and the lowest is 'F'. Consider district and island ranks also. (having an island rank above 300 or a district rank above 100 can be considered as a good result",
            "GPA or CGPA": "This is a cumulative measure of a student's academic performance, typically on a scale of 4.0. So the best is 4.0, 3.9-3.7 is good, 3.5-3.0 is average and lower than 2.0 is really poor.",
            "Projects": "List of projects undertaken, with a focus on those relevant to the job description.",
            "Work Experience": "Details of previous employment, including roles, responsibilities, and achievements.",
            "Skills": "Technical and soft skills relevant to the job description.",
            "Certifications": "Relevant certifications that enhance the candidate's qualifications for the job.",
            "GitHub": "GitHub profile showing coding activity, open-source contributions, and technical expertise. Consider: account age, number of repositories, stars received, primary languages, activity level, and quality of projects. Active contributors with original repositories and stars show strong technical engagement. For scoring: 2+ years account age with 10+ original repos and 20+ stars = strong (70-100% of max), 1-2 years with 5-10 repos and 5-20 stars = moderate (40-70% of max), <1 year with <5 repos and <5 stars = weak (0-40% of max). Consider activity (active in last 30 days = bonus) and language match with job requirements."
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
            - **For GitHub criterion**: If GitHub data is available, evaluate based on account age, repositories, stars, activity, languages, and relevance to the job. If no GitHub data is available, give 0 marks with explanation "No GitHub profile data available."
            - **Do NOT** give marks for `LinkedIn` (skip it entirely or add with mark 0/maximum and description "Not generating mark for LinkedIn").
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
              "GitHub": {{
                "mark": 4,
                "mark_fraction": "4/5",
                "explanation": "Active GitHub profile with relevant projects and strong community engagement."
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
            
            **GitHub Profile Data:**
            {github_summary}

            **Evaluation Criteria (Max Marks):**
            {criteria_object}

            **Guidance Section (Best vs. Worst Examples):**
            {guidance_section}

            Evaluate the resume based on the items specified in the criteria_object. Use only the information provided in the guidance_section for your evaluation. 
            Return the results strictly in JSON format, including each criterion with its assigned mark and a brief explanation.
            """
        # print("PROMPT::", prompt_template)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt_template)
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
