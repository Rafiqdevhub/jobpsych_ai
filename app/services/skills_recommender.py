from typing import Dict, List, Any, Set, Tuple
import re
from collections import defaultdict


class SkillsRecommender:
    """
    Advanced skills recommender that analyzes skill gaps and provides
    personalized learning recommendations.
    """

    def __init__(self):
        self.skill_categories = self._load_skill_categories()
        self.learning_resources = self._load_learning_resources()
        self.skill_progression = self._load_skill_progression()

    def _load_skill_categories(self) -> Dict[str, List[str]]:
        """Load comprehensive skill categories and their relationships."""
        return {
            "programming_languages": {
                "beginner": ["python", "javascript", "html", "css"],
                "intermediate": ["java", "c#", "php", "ruby", "go"],
                "advanced": ["c++", "rust", "scala", "haskell"]
            },
            "web_development": {
                "frontend": ["react", "angular", "vue", "typescript", "webpack"],
                "backend": ["node.js", "express", "django", "flask", "spring"],
                "fullstack": ["mern", "mean", "django-rest", "graphql"]
            },
            "data_science": {
                "basics": ["python", "pandas", "numpy", "matplotlib"],
                "ml": ["scikit-learn", "tensorflow", "pytorch", "keras"],
                "advanced": ["apache spark", "hadoop", "aws sagemaker"]
            },
            "cloud_platforms": {
                "basics": ["aws", "azure", "google cloud"],
                "services": ["ec2", "s3", "lambda", "kubernetes", "docker"],
                "advanced": ["terraform", "cloudformation", "ansible"]
            },
            "devops": {
                "tools": ["docker", "kubernetes", "jenkins", "gitlab ci"],
                "platforms": ["aws", "azure devops", "google cloud build"],
                "practices": ["ci/cd", "infrastructure as code", "monitoring"]
            },
            "databases": {
                "relational": ["mysql", "postgresql", "oracle", "sql server"],
                "nosql": ["mongodb", "redis", "cassandra", "dynamodb"],
                "querying": ["sql", "nosql", "graph databases"]
            }
        }

    def _load_learning_resources(self) -> Dict[str, Dict[str, Any]]:
        """Load learning resources for different skills."""
        return {
            "python": {
                "courses": ["Python for Everybody (Coursera)", "Automate the Boring Stuff"],
                "platforms": ["Codecademy", "freeCodeCamp", "Python.org tutorials"],
                "time_estimate": "2-3 months",
                "difficulty": "Beginner"
            },
            "javascript": {
                "courses": ["JavaScript Algorithms and Data Structures (freeCodeCamp)"],
                "platforms": ["MDN Web Docs", "JavaScript.info"],
                "time_estimate": "2-4 months",
                "difficulty": "Beginner to Intermediate"
            },
            "react": {
                "courses": ["React - The Complete Guide", "React Tutorial (official)"],
                "platforms": ["React.dev", "Codecademy"],
                "time_estimate": "1-2 months",
                "difficulty": "Intermediate"
            },
            "node.js": {
                "courses": ["Node.js Complete Guide", "Express.js Fundamentals"],
                "platforms": ["Node.js official docs", "Express.js docs"],
                "time_estimate": "1-2 months",
                "difficulty": "Intermediate"
            },
            "docker": {
                "courses": ["Docker for Beginners", "Docker Deep Dive"],
                "platforms": ["Docker Docs", "Play with Docker"],
                "time_estimate": "1-2 weeks",
                "difficulty": "Beginner to Intermediate"
            },
            "kubernetes": {
                "courses": ["Kubernetes for Beginners", "CKA Certification Prep"],
                "platforms": ["Kubernetes Docs", "Katacoda"],
                "time_estimate": "2-3 months",
                "difficulty": "Intermediate to Advanced"
            },
            "aws": {
                "courses": ["AWS Certified Cloud Practitioner", "AWS Solutions Architect"],
                "platforms": ["AWS Training", "A Cloud Guru"],
                "time_estimate": "1-3 months",
                "difficulty": "Beginner to Advanced"
            },
            "machine learning": {
                "courses": ["Machine Learning by Andrew Ng", "Deep Learning Specialization"],
                "platforms": ["Coursera", "fast.ai"],
                "time_estimate": "3-6 months",
                "difficulty": "Intermediate to Advanced"
            }
        }

    def _load_skill_progression(self) -> Dict[str, List[str]]:
        """Load skill progression paths."""
        return {
            "web_developer": [
                "html", "css", "javascript", "git", "responsive design",
                "react", "node.js", "express", "mongodb", "rest apis"
            ],
            "data_scientist": [
                "python", "statistics", "pandas", "numpy", "matplotlib",
                "scikit-learn", "sql", "machine learning", "deep learning"
            ],
            "devops_engineer": [
                "linux", "bash", "git", "docker", "kubernetes",
                "aws", "terraform", "ci/cd", "monitoring"
            ],
            "fullstack_developer": [
                "html", "css", "javascript", "react", "node.js",
                "python", "django", "postgresql", "docker", "aws"
            ]
        }

    def recommend_skills(self, resume_data: Dict[str, Any], job_data: Dict[str, Any],
                        similarity_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive skill recommendations based on gaps analysis.

        Args:
            resume_data: Parsed resume data
            job_data: Parsed job description data
            similarity_analysis: Similarity analysis results

        Returns:
            Dict containing skill recommendations and learning plan
        """
        # Identify skill gaps
        skill_gaps = self._identify_skill_gaps(resume_data, job_data, similarity_analysis)

        # Generate learning recommendations
        learning_plan = self._generate_learning_plan(skill_gaps, resume_data)

        # Calculate priority scores
        prioritized_skills = self._prioritize_skills(skill_gaps, job_data)

        # Generate timeline and milestones
        timeline = self._generate_timeline(prioritized_skills)

        return {
            "skill_gaps": skill_gaps,
            "learning_plan": learning_plan,
            "prioritized_skills": prioritized_skills,
            "timeline": timeline,
            "estimated_time": self._estimate_total_time(prioritized_skills),
            "career_path_suggestions": self._suggest_career_paths(resume_data, job_data)
        }

    def _identify_skill_gaps(self, resume_data: Dict, job_data: Dict,
                           similarity_analysis: Dict) -> List[Dict[str, Any]]:
        """Identify specific skill gaps between resume and job requirements."""
        skill_gaps = []

        resume_skills = set(skill.lower() for skill in resume_data.get('skills', []))
        job_required = set(skill.lower() for skill in job_data.get('required_skills', []))
        job_preferred = set(skill.lower() for skill in job_data.get('preferred_skills', []))

        # Required skill gaps
        missing_required = job_required - resume_skills
        for skill in missing_required:
            skill_gaps.append({
                "skill": skill.title(),
                "type": "required",
                "priority": "high",
                "reason": "Essential for the job role",
                "category": self._categorize_skill(skill)
            })

        # Preferred skill gaps
        missing_preferred = job_preferred - resume_skills
        for skill in missing_preferred:
            skill_gaps.append({
                "skill": skill.title(),
                "type": "preferred",
                "priority": "medium",
                "reason": "Would strengthen candidacy",
                "category": self._categorize_skill(skill)
            })

        # Additional gaps based on job responsibilities
        responsibility_gaps = self._analyze_responsibility_gaps(resume_data, job_data)
        skill_gaps.extend(responsibility_gaps)

        return skill_gaps

    def _analyze_responsibility_gaps(self, resume_data: Dict, job_data: Dict) -> List[Dict[str, Any]]:
        """Analyze job responsibilities to identify additional skill gaps."""
        gaps = []

        responsibilities = job_data.get('responsibilities', [])
        resume_experience = ' '.join(resume_data.get('experience', [])).lower()

        # Map responsibilities to potential skills
        responsibility_skill_map = {
            "design": ["ui/ux design", "figma", "adobe xd", "prototyping"],
            "database": ["sql", "nosql", "database design", "optimization"],
            "api": ["rest", "graphql", "api design", "documentation"],
            "testing": ["unit testing", "integration testing", "tdd", "selenium"],
            "security": ["owasp", "encryption", "authentication", "authorization"],
            "performance": ["optimization", "caching", "monitoring", "profiling"],
            "deployment": ["ci/cd", "docker", "kubernetes", "cloud platforms"],
            "collaboration": ["git", "agile", "scrum", "jira", "confluence"]
        }

        for responsibility in responsibilities:
            resp_lower = responsibility.lower()

            for key, skills in responsibility_skill_map.items():
                if key in resp_lower:
                    for skill in skills:
                        if skill not in resume_experience:
                            gaps.append({
                                "skill": skill.title(),
                                "type": "responsibility-based",
                                "priority": "medium",
                                "reason": f"Needed for: {responsibility[:50]}...",
                                "category": self._categorize_skill(skill)
                            })

        return gaps

    def _generate_learning_plan(self, skill_gaps: List[Dict], resume_data: Dict) -> Dict[str, Any]:
        """Generate a structured learning plan for skill gaps."""
        learning_plan = {
            "immediate_actions": [],
            "short_term_goals": [],
            "long_term_goals": [],
            "resources": [],
            "projects": []
        }

        current_skills = set(skill.lower() for skill in resume_data.get('skills', []))

        for gap in skill_gaps:
            skill = gap['skill'].lower()
            priority = gap['priority']

            # Get learning resources for this skill
            resources = self.learning_resources.get(skill, {})

            if priority == "high":
                learning_plan["immediate_actions"].append({
                    "skill": gap['skill'],
                    "action": f"Start learning {gap['skill']}",
                    "resources": resources,
                    "timeframe": "1-2 weeks"
                })
            elif priority == "medium":
                learning_plan["short_term_goals"].append({
                    "skill": gap['skill'],
                    "action": f"Build proficiency in {gap['skill']}",
                    "resources": resources,
                    "timeframe": "1-3 months"
                })
            else:
                learning_plan["long_term_goals"].append({
                    "skill": gap['skill'],
                    "action": f"Master {gap['skill']}",
                    "resources": resources,
                    "timeframe": "3-6 months"
                })

            # Add to resources if available
            if resources:
                learning_plan["resources"].append({
                    "skill": gap['skill'],
                    "courses": resources.get('courses', []),
                    "platforms": resources.get('platforms', []),
                    "difficulty": resources.get('difficulty', 'Unknown')
                })

        # Generate project suggestions
        learning_plan["projects"] = self._suggest_projects(skill_gaps, current_skills)

        return learning_plan

    def _suggest_projects(self, skill_gaps: List[Dict], current_skills: Set[str]) -> List[Dict[str, Any]]:
        """Suggest practical projects to build the missing skills."""
        projects = []

        # Project templates based on skill categories
        project_templates = {
            "web": [
                "Build a personal portfolio website",
                "Create a task management app",
                "Develop a blog platform",
                "Build an e-commerce site"
            ],
            "data": [
                "Create a data visualization dashboard",
                "Build a recommendation system",
                "Develop a predictive model",
                "Analyze a public dataset"
            ],
            "devops": [
                "Set up CI/CD pipeline",
                "Containerize an application",
                "Deploy app to cloud platform",
                "Implement monitoring solution"
            ],
            "api": [
                "Build a REST API",
                "Create a GraphQL API",
                "Develop API documentation",
                "Implement authentication"
            ]
        }

        for gap in skill_gaps[:5]:  # Limit to top 5 gaps
            skill = gap['skill'].lower()
            category = gap.get('category', '')

            # Find relevant project templates
            relevant_projects = []
            for cat, templates in project_templates.items():
                if cat in category.lower() or cat in skill:
                    relevant_projects.extend(templates)

            if relevant_projects:
                projects.append({
                    "skill": gap['skill'],
                    "project": relevant_projects[0],  # Take first relevant project
                    "difficulty": "Beginner" if gap['priority'] == "high" else "Intermediate",
                    "estimated_time": "2-4 weeks"
                })

        return projects

    def _prioritize_skills(self, skill_gaps: List[Dict], job_data: Dict) -> List[Dict[str, Any]]:
        """Prioritize skills based on job requirements and difficulty."""
        prioritized = []

        for gap in skill_gaps:
            priority_score = self._calculate_priority_score(gap, job_data)
            gap['priority_score'] = priority_score
            prioritized.append(gap)

        # Sort by priority score (descending)
        prioritized.sort(key=lambda x: x['priority_score'], reverse=True)

        return prioritized

    def _calculate_priority_score(self, gap: Dict, job_data: Dict) -> float:
        """Calculate priority score for a skill gap."""
        base_score = 0.0

        # Base score from type
        if gap['type'] == 'required':
            base_score = 1.0
        elif gap['type'] == 'preferred':
            base_score = 0.7
        else:
            base_score = 0.5

        # Adjust based on learning difficulty
        skill = gap['skill'].lower()
        resources = self.learning_resources.get(skill, {})
        difficulty = resources.get('difficulty', 'Intermediate')

        if difficulty == 'Beginner':
            difficulty_multiplier = 1.0
        elif difficulty == 'Intermediate':
            difficulty_multiplier = 0.8
        else:
            difficulty_multiplier = 0.6

        # Adjust based on time estimate
        time_estimate = resources.get('time_estimate', '2-3 months')
        if '1-2 weeks' in time_estimate:
            time_multiplier = 1.2
        elif '1-2 months' in time_estimate:
            time_multiplier = 1.0
        elif '3-6 months' in time_estimate:
            time_multiplier = 0.8
        else:
            time_multiplier = 0.9

        return base_score * difficulty_multiplier * time_multiplier

    def _generate_timeline(self, prioritized_skills: List[Dict]) -> Dict[str, Any]:
        """Generate a learning timeline with milestones."""
        timeline = {
            "week_1_2": [],
            "month_1_2": [],
            "month_3_6": [],
            "milestones": []
        }

        for i, skill in enumerate(prioritized_skills[:10]):  # Top 10 skills
            if i < 3:
                timeline["week_1_2"].append(skill['skill'])
            elif i < 6:
                timeline["month_1_2"].append(skill['skill'])
            else:
                timeline["month_3_6"].append(skill['skill'])

        # Generate milestones
        timeline["milestones"] = [
            {
                "week": 2,
                "achievement": f"Complete basics of {', '.join(timeline['week_1_2'][:2])}"
            },
            {
                "month": 1,
                "achievement": f"Build first project using {timeline['month_1_2'][0] if timeline['month_1_2'] else 'learned skills'}"
            },
            {
                "month": 3,
                "achievement": "Complete portfolio project demonstrating new skills"
            },
            {
                "month": 6,
                "achievement": "Achieve proficiency in all targeted skills"
            }
        ]

        return timeline

    def _estimate_total_time(self, prioritized_skills: List[Dict]) -> str:
        """Estimate total time needed to learn all prioritized skills."""
        total_weeks = 0

        for skill in prioritized_skills[:8]:  # Top 8 skills
            skill_name = skill['skill'].lower()
            resources = self.learning_resources.get(skill_name, {})
            time_estimate = resources.get('time_estimate', '2-3 months')

            # Parse time estimate
            if 'weeks' in time_estimate:
                weeks = int(re.search(r'(\d+)', time_estimate).group(1))
            elif 'months' in time_estimate:
                months = int(re.search(r'(\d+)', time_estimate).group(1))
                weeks = months * 4
            else:
                weeks = 8  # Default 2 months

            total_weeks += weeks

        # Convert to readable format
        if total_weeks <= 8:
            return f"{total_weeks} weeks"
        else:
            months = total_weeks // 4
            remaining_weeks = total_weeks % 4
            if remaining_weeks:
                return f"{months} months, {remaining_weeks} weeks"
            else:
                return f"{months} months"

    def _suggest_career_paths(self, resume_data: Dict, job_data: Dict) -> List[Dict[str, Any]]:
        """Suggest alternative career paths based on current skills."""
        suggestions = []

        current_skills = set(skill.lower() for skill in resume_data.get('skills', []))
        job_title = job_data.get('job_title', '').lower()

        # Career path suggestions based on current skills
        if 'python' in current_skills:
            if 'data' in job_title or 'machine learning' in current_skills:
                suggestions.append({
                    "path": "Data Scientist / ML Engineer",
                    "reason": "Strong Python foundation with data skills",
                    "next_steps": ["Learn advanced ML", "Get certifications", "Build portfolio"]
                })
            elif 'web' in job_title or 'django' in current_skills or 'flask' in current_skills:
                suggestions.append({
                    "path": "Python Web Developer",
                    "reason": "Python web development experience",
                    "next_steps": ["Master Django/Flask", "Learn frontend", "Deploy applications"]
                })

        if 'javascript' in current_skills:
            suggestions.append({
                "path": "Full Stack JavaScript Developer",
                "reason": "JavaScript proficiency",
                "next_steps": ["Learn React/Node.js", "Build full-stack apps", "Master modern JS"]
            })

        if 'docker' in current_skills or 'kubernetes' in current_skills:
            suggestions.append({
                "path": "DevOps Engineer",
                "reason": "Container and orchestration experience",
                "next_steps": ["Learn cloud platforms", "Get DevOps certs", "Master CI/CD"]
            })

        return suggestions[:3]  # Top 3 suggestions

    def _categorize_skill(self, skill: str) -> str:
        """Categorize a skill into a broader category."""
        skill_lower = skill.lower()

        for category, subcategories in self.skill_categories.items():
            for subcategory, skills in subcategories.items():
                if skill_lower in skills:
                    return f"{category} - {subcategory}"

        # Fallback categorization
        if any(word in skill_lower for word in ['python', 'java', 'javascript', 'c++', 'ruby']):
            return "programming_languages"
        elif any(word in skill_lower for word in ['react', 'angular', 'vue', 'html', 'css']):
            return "web_development"
        elif any(word in skill_lower for word in ['aws', 'azure', 'docker', 'kubernetes']):
            return "cloud_platforms"
        else:
            return "other"
