import re
import os
from pathlib import Path
from typing import Dict, List, Tuple, Set
from bs4 import BeautifulSoup
import json

class ValidationError:
    def __init__(self, file_name: str, error_type: str, description: str, suggested_fix: str = ""):
        self.file_name = file_name
        self.error_type = error_type
        self.description = description
        self.suggested_fix = suggested_fix
    
    def __str__(self):
        return f"{self.file_name}: {self.error_type} - {self.description}"

class CodeValidator:
    def __init__(self, folder_path: str):
        self.folder_path = Path(folder_path)
        self.files = {}
        self.errors = []
        
    def load_files(self):
        """Load all files in the folder for validation"""
        for file_path in self.folder_path.glob("*"):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.files[file_path.name] = f.read()
                except Exception as e:
                    self.errors.append(ValidationError(
                        file_path.name, 
                        "READ_ERROR", 
                        f"Could not read file: {e}"
                    ))
    
    def validate_all(self) -> List[ValidationError]:
        """Run all validation checks and return errors"""
        self.load_files()
        self.errors = []
        
        # Run validation checks
        self._validate_file_references()
        self._validate_html_structure()
        self._validate_css_selectors()
        self._validate_js_selectors()
        self._validate_syntax()
        
        return self.errors
    
    def _validate_file_references(self):
        """Check if all file references (src, href) exist"""
        all_files = set(self.files.keys())
        
        for file_name, content in self.files.items():
            if file_name.endswith(('.html', '.htm')):
                # Check script src
                script_refs = re.findall(r'<script[^>]+src=["\'](.*?)["\']', content, re.IGNORECASE)
                for ref in script_refs:
                    if ref not in all_files and not ref.startswith(('http', '//')):
                        # Try to find a JS file that should be renamed
                        js_files = [f for f in all_files if f.endswith('.js')]
                        if len(js_files) == 1:
                            self.errors.append(ValidationError(
                                file_name,
                                "MISMATCHED_SCRIPT_REF",
                                f"Script reference '{ref}' not found. Found JS file: {js_files[0]}",
                                f"Rename {js_files[0]} to {ref}"
                            ))
                        else:
                            self.errors.append(ValidationError(
                                file_name,
                                "MISSING_SCRIPT",
                                f"Script reference '{ref}' not found in project files",
                                f"Create {ref} or update reference to existing JS file"
                            ))
                
                # Check link href (CSS)
                link_refs = re.findall(r'<link[^>]+href=["\'](.*?)["\']', content, re.IGNORECASE)
                for ref in link_refs:
                    if ref not in all_files and not ref.startswith(('http', '//')):
                        self.errors.append(ValidationError(
                            file_name,
                            "MISSING_STYLESHEET",
                            f"Stylesheet reference '{ref}' not found in project files",
                            f"Create {ref} or update reference to existing CSS file"
                        ))
                
                # Check img src
                img_refs = re.findall(r'<img[^>]+src=["\'](.*?)["\']', content, re.IGNORECASE)
                for ref in img_refs:
                    if ref not in all_files and not ref.startswith(('http', '//', 'data:')):
                        self.errors.append(ValidationError(
                            file_name,
                            "MISSING_IMAGE",
                            f"Image reference '{ref}' not found in project files",
                            f"Add {ref} to project or update reference"
                        ))
    
    def _validate_html_structure(self):
        """Validate HTML structure and common issues"""
        for file_name, content in self.files.items():
            if file_name.endswith(('.html', '.htm')):
                try:
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Check for basic HTML structure
                    if not soup.find('html'):
                        self.errors.append(ValidationError(
                            file_name, "MISSING_HTML_TAG", "Missing <html> tag"
                        ))
                    
                    if not soup.find('head'):
                        self.errors.append(ValidationError(
                            file_name, "MISSING_HEAD_TAG", "Missing <head> tag"
                        ))
                        
                    if not soup.find('body'):
                        self.errors.append(ValidationError(
                            file_name, "MISSING_BODY_TAG", "Missing <body> tag"
                        ))
                    
                    # Check for duplicate IDs
                    ids = [elem.get('id') for elem in soup.find_all(id=True)]
                    duplicate_ids = [id for id in set(ids) if ids.count(id) > 1]
                    for dup_id in duplicate_ids:
                        self.errors.append(ValidationError(
                            file_name, "DUPLICATE_ID", f"Duplicate ID: {dup_id}"
                        ))
                        
                except Exception as e:
                    self.errors.append(ValidationError(
                        file_name, "HTML_PARSE_ERROR", f"Could not parse HTML: {e}"
                    ))
    
    def _validate_css_selectors(self):
        """Validate CSS selectors against HTML elements"""
        html_elements = self._extract_html_elements()
        
        for file_name, content in self.files.items():
            if file_name.endswith('.css'):
                css_selectors = self._extract_css_selectors(content)
                
                for selector in css_selectors:
                    if not self._selector_matches_html(selector, html_elements):
                        self.errors.append(ValidationError(
                            file_name,
                            "UNUSED_CSS_SELECTOR",
                            f"CSS selector '{selector}' doesn't match any HTML elements",
                            f"Remove selector or add matching HTML element"
                        ))
    
    def _validate_js_selectors(self):
        """Validate JavaScript selectors against HTML elements"""
        html_elements = self._extract_html_elements()
        
        for file_name, content in self.files.items():
            if file_name.endswith('.js'):
                js_selectors = self._extract_js_selectors(content)
                
                for selector_type, selector in js_selectors:
                    if not self._js_selector_matches_html(selector_type, selector, html_elements):
                        self.errors.append(ValidationError(
                            file_name,
                            "MISSING_HTML_ELEMENT",
                            f"JavaScript selector '{selector}' (type: {selector_type}) doesn't match any HTML elements",
                            f"Add HTML element with {selector_type}='{selector}'"
                        ))
    
    def _validate_syntax(self):
        """Basic syntax validation"""
        for file_name, content in self.files.items():
            if file_name.endswith('.js'):
                # Check for common JS syntax errors
                if content.count('{') != content.count('}'):
                    self.errors.append(ValidationError(
                        file_name, "MISMATCHED_BRACES", "Mismatched curly braces"
                    ))
                
                if content.count('(') != content.count(')'):
                    self.errors.append(ValidationError(
                        file_name, "MISMATCHED_PARENTHESES", "Mismatched parentheses"
                    ))
            
            elif file_name.endswith('.css'):
                # Check CSS syntax
                if content.count('{') != content.count('}'):
                    self.errors.append(ValidationError(
                        file_name, "MISMATCHED_CSS_BRACES", "Mismatched CSS braces"
                    ))
    
    def _extract_html_elements(self) -> Dict[str, Set[str]]:
        """Extract IDs, classes, and tags from HTML files"""
        elements = {'ids': set(), 'classes': set(), 'tags': set()}
        
        for file_name, content in self.files.items():
            if file_name.endswith(('.html', '.htm')):
                try:
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Extract IDs
                    for elem in soup.find_all(id=True):
                        elements['ids'].add(elem.get('id'))
                    
                    # Extract classes
                    for elem in soup.find_all(class_=True):
                        classes = elem.get('class')
                        if isinstance(classes, list):
                            elements['classes'].update(classes)
                        else:
                            elements['classes'].add(classes)
                    
                    # Extract tags
                    for elem in soup.find_all():
                        elements['tags'].add(elem.name.lower())
                        
                except Exception:
                    pass
        
        return elements
    
    def _extract_css_selectors(self, css_content: str) -> List[str]:
        """Extract selectors from CSS content"""
        selectors = []
        
        # Simple regex to find CSS selectors
        css_rules = re.findall(r'([^{}]+)\s*{[^}]*}', css_content)
        
        for rule in css_rules:
            # Clean up the selector
            selector = rule.strip()
            if selector and not selector.startswith('@'):
                selectors.append(selector)
        
        return selectors
    
    def _extract_js_selectors(self, js_content: str) -> List[Tuple[str, str]]:
        """Extract DOM selectors from JavaScript content"""
        selectors = []
        
        # getElementById
        id_matches = re.findall(r'getElementById\(["\']([^"\']+)["\']\)', js_content)
        for match in id_matches:
            selectors.append(('id', match))
        
        # getElementsByClassName
        class_matches = re.findall(r'getElementsByClassName\(["\']([^"\']+)["\']\)', js_content)
        for match in class_matches:
            selectors.append(('class', match))
        
        # querySelector with ID
        query_id_matches = re.findall(r'querySelector\(["\']#([^"\']+)["\']\)', js_content)
        for match in query_id_matches:
            selectors.append(('id', match))
        
        # querySelector with class
        query_class_matches = re.findall(r'querySelector\(["\']\.([^"\']+)["\']\)', js_content)
        for match in query_class_matches:
            selectors.append(('class', match))
        
        return selectors
    
    def _selector_matches_html(self, selector: str, html_elements: Dict[str, Set[str]]) -> bool:
        """Check if CSS selector matches HTML elements"""
        selector = selector.strip()
        
        # Simple tag selector
        if selector in html_elements['tags']:
            return True
        
        # ID selector
        if selector.startswith('#'):
            id_name = selector[1:]
            return id_name in html_elements['ids']
        
        # Class selector
        if selector.startswith('.'):
            class_name = selector[1:]
            return class_name in html_elements['classes']
        
        # For complex selectors, just return True for now
        if ' ' in selector or '>' in selector or '+' in selector or '~' in selector:
            return True
        
        return False
    
    def _js_selector_matches_html(self, selector_type: str, selector: str, html_elements: Dict[str, Set[str]]) -> bool:
        """Check if JavaScript selector matches HTML elements"""
        if selector_type == 'id':
            return selector in html_elements['ids']
        elif selector_type == 'class':
            return selector in html_elements['classes']
        
        return False
    
    def generate_fix_prompt(self) -> str:
        """Generate a prompt for LLM to fix the detected errors"""
        if not self.errors:
            return ""
        
        prompt = "The generated code has the following errors that need to be fixed:\n\n"
        
        for error in self.errors:
            prompt += f"• {error.file_name}: {error.description}\n"
            if error.suggested_fix:
                prompt += f"  Suggested fix: {error.suggested_fix}\n"
        
        prompt += "\nPlease generate corrected versions of the affected files as markdown code blocks. "
        prompt += "Make sure all file references are correct and all selectors match existing HTML elements. "
        prompt += "Only output the corrected code blocks, no explanations."
        
        return prompt