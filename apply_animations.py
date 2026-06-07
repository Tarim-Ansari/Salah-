#!/usr/bin/env python3
"""
Script to automatically add animation classes to all SALAH HTML templates.
Run this script from the project root directory.
"""

import os
import re

# Define the templates directory
TEMPLATES_DIR = "accounts/templates/accounts"

# Animation CSS link to add
ANIMATION_CSS_LINK = """    
    <!-- Animation CSS -->
    <link rel="stylesheet" href="{% static 'accounts/css/animations.css' %}">
"""

def add_animation_css_link(content):
    """Add animation CSS link after fonts link in <head>"""
    # Look for the fonts link and add animation CSS after it
    pattern = r'(<!-- Professional Fonts -->.*?rel="stylesheet">)'
    replacement = r'\1' + ANIMATION_CSS_LINK
    return re.sub(pattern, replacement, content, flags=re.DOTALL)

def add_navbar_animation(content):
    """Add navbar-animate class to navbar"""
    content = re.sub(
        r'<header class="navbar"',
        r'<header class="navbar navbar-animate"',
        content
    )
    return content

def add_button_animations(content):
    """Add btn-animate to all buttons"""
    # Match buttons that don't already have btn-animate
    content = re.sub(
        r'class="btn([^"]*?)"(?![^<]*btn-animate)',
        r'class="btn\1 btn-animate"',
        content
    )
    return content

def add_card_animations(content):
    """Add card animations to various card types"""
    # Request cards
    content = re.sub(
        r'class="request-card"',
        r'class="request-card card-animate hover-lift animate-fade-in"',
        content
    )
    # Consultation cards
    content = re.sub(
        r'class="consultation-card"',
        r'class="consultation-card card-animate hover-lift animate-fade-in"',
        content
    )
    # Lawyer cards
    content = re.sub(
        r'class="lawyer-card"',
        r'class="lawyer-card card-animate hover-lift animate-scale-in"',
        content
    )
    # Service cards
    content = re.sub(
        r'class="service-card"',
        r'class="service-card card-animate hover-lift animate-scale-in"',
        content
    )
    # Feature cards
    content = re.sub(
        r'class="feature-card"',
        r'class="feature-card card-animate hover-lift animate-scale-in"',
        content
    )
    # Stat cards
    content = re.sub(
        r'class="stat-card"',
        r'class="stat-card card-animate hover-lift animate-scale-in"',
        content
    )
    # Transaction cards
    content = re.sub(
        r'class="transaction-card"',
        r'class="transaction-card card-animate hover-lift animate-fade-in"',
        content
    )
    # Role cards
    content = re.sub(
        r'class="role-card"',
        r'class="role-card card-animate hover-glow animate-scale-in"',
        content
    )
    return content

def add_input_animations(content):
    """Add input-animate to form inputs"""
    # Text inputs
    content = re.sub(
        r'<input([^>]*?)type="text"',
        r'<input\1type="text" class="input-animate"',
        content
    )
    # Email inputs
    content = re.sub(
        r'<input([^>]*?)type="email"',
        r'<input\1type="email" class="input-animate"',
        content
    )
    # Password inputs
    content = re.sub(
        r'<input([^>]*?)type="password"',
        r'<input\1type="password" class="input-animate"',
        content
    )
    # Textareas
    content = re.sub(
        r'<textarea',
        r'<textarea class="input-animate"',
        content
    )
    # Selects
    content = re.sub(
        r'<select',
        r'<select class="input-animate"',
        content
    )
    return content

def add_title_animations(content):
    """Add fade-in-down to page titles"""
    content = re.sub(
        r'<h1([^>]*)>',
        r'<h1\1 class="animate-fade-in-down">',
        content
    )
    return content

def process_file(filepath):
    """Process a single HTML file"""
    print(f"Processing: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already has animations.css
        if 'animations.css' in content:
            print(f"  ✓ Already has animations, skipping")
            return
        
        # Apply transformations
        original_content = content
        content = add_animation_css_link(content)
        content = add_navbar_animation(content)
        content = add_button_animations(content)
        content = add_card_animations(content)
        content = add_input_animations(content)
        content = add_title_animations(content)
        
        # Only write if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  [OK] Animations added successfully")
        else:
            print(f"  [-] No changes needed")
            
    except Exception as e:
        print(f"  [ERROR] Error: {e}")

def main():
    """Main function to process all HTML files"""
    print("=" * 60)
    print("SALAH Animation Applicator")
    print("=" * 60)
    print()
    
    # Find all HTML files
    html_files = []
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                html_files.append(filepath)
    
    print(f"Found {len(html_files)} HTML files")
    print()
    
    # Process each file
    for filepath in sorted(html_files):
        process_file(filepath)
        print()
    
    print("=" * 60)
    print("[SUCCESS] Animation application complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Test the website in your browser")
    print("2. Check that animations work smoothly")
    print("3. Verify no layout breaks occurred")
    print()

if __name__ == "__main__":
    main()

# Made with Bob
