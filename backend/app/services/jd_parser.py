from __future__ import annotations

import re
from typing import List, Set
from html import unescape
from bs4 import BeautifulSoup


# 常见技术技能关键词
TECH_SKILLS_KEYWORDS = {
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'kotlin', 'swift',
    'php', 'ruby', 'scala', 'r', 'matlab', 'perl', 'shell', 'bash', 'powershell',
    
    # Web Technologies
    'react', 'vue', 'angular', 'node.js', 'express', 'django', 'flask', 'fastapi', 'spring',
    'html', 'css', 'sass', 'less', 'webpack', 'vite', 'next.js', 'nuxt.js',
    
    # Databases
    'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra',
    'oracle', 'sqlite', 'dynamodb', 'neo4j',
    
    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins',
    'ci/cd', 'git', 'github', 'gitlab', 'terraform', 'cloudformation',
    
    # Data & ML
    'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras', 'scikit-learn',
    'pandas', 'numpy', 'spark', 'hadoop', 'kafka', 'airflow', 'data science',
    
    # Tools & Frameworks
    'rest api', 'graphql', 'microservices', 'agile', 'scrum', 'jira', 'confluence',
    'linux', 'unix', 'windows', 'macos',
    
    # Frontend
    'responsive design', 'ui/ux', 'figma', 'adobe', 'photoshop', 'illustrator',
    
    # Backend
    'api development', 'serverless', 'lambda', 'api gateway', 'load balancing',
}


def clean_html(text: str) -> str:
    """清理HTML标签，保留文本内容，处理编码问题避免乱码"""
    if not text:
        return ""
    
    # 尝试检测和处理编码
    if isinstance(text, bytes):
        # 如果是字节，尝试解码
        try:
            text = text.decode('utf-8')
        except UnicodeDecodeError:
            try:
                text = text.decode('latin-1')
            except UnicodeDecodeError:
                text = text.decode('utf-8', errors='ignore')
    
    # 使用BeautifulSoup解析HTML，指定编码
    try:
        soup = BeautifulSoup(text, 'html.parser', from_encoding='utf-8')
    except:
        soup = BeautifulSoup(text, 'html.parser')
    
    # 移除script和style标签
    for script in soup(["script", "style", "meta", "link", "noscript"]):
        script.decompose()
    
    # 获取文本并清理
    text = soup.get_text(separator=' ', strip=True)
    
    # 解码HTML实体
    text = unescape(text)
    
    # 清理特殊字符和乱码
    # 移除控制字符（除了换行和制表符）
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # 清理多余的空白字符
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    # 移除常见的乱码模式（保留更多有效字符）
    # 保留字母、数字、常见标点、空格、换行
    text = re.sub(r'[^\w\s\-.,;:!?()\[\]{}\'"@#$%&*+=/\\|<>~`–—•·•]', ' ', text, flags=re.UNICODE)
    
    # 清理连续的标点符号
    text = re.sub(r'[.,;:!?]{2,}', '.', text)
    
    # 再次清理多余空白
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 移除开头和结尾的标点
    text = re.sub(r'^[^\w]+|[^\w]+$', '', text)
    
    return text


def extract_key_skills(jd_text: str) -> List[str]:
    """
    从JD文本中提取关键技能
    
    Args:
        jd_text: 职位描述文本
        
    Returns:
        技能列表（去重、排序）
    """
    if not jd_text:
        return []
    
    # 清理文本
    text = clean_html(jd_text).lower()
    
    # 找到的技能
    found_skills: Set[str] = set()
    
    # 匹配技能关键词
    for skill in TECH_SKILLS_KEYWORDS:
        # 使用单词边界匹配，避免部分匹配
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            found_skills.add(skill)
    
    # 查找常见的技能模式
    # 例如: "Experience with Python, Java, and React"
    skill_patterns = [
        r'(?:proficient|experienced|skilled|knowledge|expertise|familiar).*?(?:with|in)\s+([a-z\s+]+)',
        r'(?:required|preferred|must have|nice to have).*?([a-z\s+]+)',
    ]
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # 清理匹配结果
            words = match.strip().split()
            for word in words:
                if word in TECH_SKILLS_KEYWORDS:
                    found_skills.add(word)
    
    # 查找技术栈列表（通常在"Requirements"或"Qualifications"部分）
    # 例如: "Python, JavaScript, React, Node.js"
    list_pattern = r'(?:python|java|javascript|react|node|angular|vue|typescript|c\+\+|c#|go|rust|kotlin|swift|php|ruby|scala|sql|mysql|postgresql|mongodb|redis|aws|azure|gcp|docker|kubernetes)[\s,;|]+'
    list_matches = re.findall(list_pattern, text, re.IGNORECASE)
    for match in list_matches:
        skill = match.strip().rstrip(',;|')
        if skill in TECH_SKILLS_KEYWORDS:
            found_skills.add(skill)
    
    # 返回排序后的技能列表
    return sorted(list(found_skills))


def process_jd(jd_text: str) -> dict:
    """
    处理JD文本，提取关键信息和技能
    
    Args:
        jd_text: 原始JD文本
        
    Returns:
        {
            "processed_jd": str,  # 清理后的JD文本
            "key_skills": List[str],  # 提取的技能列表
            "summary": str,  # JD摘要（前500字符）
        }
    """
    if not jd_text:
        return {
            "processed_jd": "",
            "key_skills": [],
            "summary": "",
        }
    
    # 清理HTML和格式化
    processed_jd = clean_html(jd_text)
    
    # 提取关键技能
    key_skills = extract_key_skills(processed_jd)
    
    # 生成摘要（前500字符）
    summary = processed_jd[:500] + "..." if len(processed_jd) > 500 else processed_jd
    
    # 移除常见的噪音文本
    noise_patterns = [
        r'apply now.*',
        r'click here.*',
        r'equal opportunity.*',
        r'we are an equal.*',
    ]
    
    for pattern in noise_patterns:
        processed_jd = re.sub(pattern, '', processed_jd, flags=re.IGNORECASE | re.DOTALL)
    
    # 清理多余的空白
    processed_jd = re.sub(r'\s+', ' ', processed_jd).strip()
    
    return {
        "processed_jd": processed_jd,
        "key_skills": key_skills,
        "summary": summary,
    }






