#!/usr/bin/env python3
import os
import json

def detect_language():
    # Check for common language-specific files
    if os.path.exists("pom.xml") or os.path.exists("build.gradle"):
        return "java"
    elif os.path.exists("go.mod"):
        return "go"
    elif os.path.exists("requirements.txt") or os.path.exists("pyproject.toml"):
        return "python"
    elif os.path.exists("package.json"):
        return "node"
    return None

def get_version(language):
    # Extract version where possible, fallback to sensible defaults
    if language == "java":
        return "17"  # Could parse pom.xml for specifics
    elif language == "go":
        return "1.21"  # Could parse go.mod
    elif language == "python":
        return "3.11"  # Could parse requirements.txt
    elif language == "node":
        with open("package.json") as f:
            data = json.load(f)
            return data.get("engines", {}).get("node", "20")
    return ""

def generate_dockerfile(language, version):
    templates = {
        "java": f"""FROM openjdk:{version}-jdk-slim
WORKDIR /app
COPY . .
RUN ./mvnw package -DskipTests
EXPOSE 8080
CMD ["java", "-jar", "target/*.jar"]
""",
        "go": f"""FROM golang:{version}-alpine
WORKDIR /app
COPY . .
RUN go build -o main
EXPOSE 8080
CMD ["./main"]
""",
        "python": f"""FROM python:{version}-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "app.py"]
""",
        "node": f"""FROM node:{version}-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
"""
    }
    if language not in templates:
        raise ValueError("Unsupported language")
    with open("Dockerfile", "w") as f:
        f.write(templates[language])

def main():
    language = detect_language()
    if not language:
        print("Couldn’t detect project type. Add a manual hint or supported files.")
        exit(1)
    version = get_version(language)
    generate_dockerfile(language, version)
    print(f"Generated Dockerfile for {language} with version {version}")

if __name__ == "__main__":
    main()