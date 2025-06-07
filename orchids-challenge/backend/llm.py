import os
from anthropic import Anthropic
from dotenv import load_dotenv
import logging
import re

load_dotenv()

logger = logging.getLogger(__name__)

# Check if API key is loaded
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    logger.error("ANTHROPIC_API_KEY not found in environment variables")
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

logger.info(f"API key loaded: {'Yes' if api_key else 'No'}")

try:
    client = Anthropic(api_key=api_key)
    logger.info("Anthropic client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Anthropic client: {e}")
    raise


def reduce_context(context: str, max_chars: int = 8000) -> str:
    """
    Intelligently reduce context while preserving the most important design information
    """
    if len(context) <= max_chars:
        return context
    
    # Extract background information specifically (highest priority)
    background_patterns = [
        r'background-color[^;]*;',
        r'background[^;]*;',
        r'body[^}]*background[^}]*}',
        r'html[^}]*background[^}]*}',
        r'\.bg-[^}]*}',
        r'background:\s*[^;]+;'
    ]
    
    background_info = []
    for pattern in background_patterns:
        matches = re.findall(pattern, context, re.IGNORECASE | re.DOTALL)
        background_info.extend(matches[:5])
    
    # Extract body/html tag styling specifically
    body_html_matches = re.findall(r'(body|html)\s*{[^}]*}', context, re.IGNORECASE | re.DOTALL)
    
    # Get all color values
    color_matches = re.findall(r'#[0-9a-fA-F]{3,6}|rgb\([^)]+\)|rgba\([^)]+\)|hsl\([^)]+\)', context)
    color_info = list(set(color_matches[:15]))
    
    # Get font information
    font_matches = re.findall(r'font-family:[^;]+;|font-size:[^;]+;|font-weight:[^;]+;', context, re.IGNORECASE)
    font_info = list(set(font_matches[:8]))
    
    # Extract other key sections
    important_patterns = [
        r'header[^}]*}',
        r'nav[^}]*}', 
        r'button[^}]*}',
        r'\.main[^}]*}',
        r'\.container[^}]*}',
    ]
    
    other_styles = []
    for pattern in important_patterns:
        matches = re.findall(pattern, context, re.IGNORECASE)
        other_styles.extend(matches[:2])
    
    # Combine with background info prioritized
    reduced_context = f"""
        CRITICAL BACKGROUND INFO:
        {'; '.join(background_info[:8])}

        BODY/HTML STYLES:
        {'; '.join(body_html_matches[:3])}

        COLORS USED:
        {', '.join(color_info[:12])}

        FONTS:
        {'; '.join(font_info[:5])}

        OTHER KEY STYLES:
        {'; '.join(other_styles[:5])}

        IMPORTANT: Match the exact background color from the screenshot. Pay special attention to body/html background styling.
        """
    
    return reduced_context[:max_chars]


def generate_clone_html(context: str, screenshot) -> str:
    """
    Generate HTML that accurately clones the visual design of the scraped website
    """
    logger.info("Starting HTML generation with enhanced visual cloning")
    logger.info(f"Original context length: {len(context)} characters")
    
    # Reduce context to manageable size
    reduced_context = reduce_context(context, max_chars=3000)
    logger.info(f"Reduced context length: {len(reduced_context)} characters")
    
    # Much shorter, screenshot-focused prompt with background emphasis
    prompt = f"""Analyze the screenshot and create an exact HTML clone.

    {reduced_context}

    Create pixel-perfect HTML with:
    - EXACT background color from screenshot (most important!)
    - Match all colors, fonts, and layout precisely
    - Inline CSS only, complete standalone document
    - Focus on body/html background styling

    Return only HTML code."""

    try:
        logger.info("Sending request to Anthropic API...")
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=0.1,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": screenshot
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        
        logger.info("Received response from Anthropic API")
        
        html_content = message.content[0].text
        logger.info(f"Generated HTML length: {len(html_content)} characters")
        
        # Clean up the response
        html_content = html_content.strip()
        
        # Remove markdown code blocks if present
        if html_content.startswith('```html'):
            html_content = html_content[7:]
        if html_content.startswith('```'):
            html_content = html_content[3:]
        if html_content.endswith('```'):
            html_content = html_content[:-3]
        
        html_content = html_content.strip()
        
        # Basic validation
        if not html_content.lower().startswith('<!doctype') and not html_content.lower().startswith('<html'):
            if not html_content.lower().startswith('<html'):
                html_content = f"""<!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Cloned Website</title>
                </head>
                <body>
                    {html_content}
                </body>
                </html>"""
        
        logger.info("HTML generation completed successfully")
        return html_content
        

    except Exception as e:
        logger.error(f"Error in enhanced LLM generation: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        
        # Return a more sophisticated fallback HTML
        fallback_html = f"""<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Clone Generation Error</title>
                <style>
                    body {{ 
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        margin: 0;
                        padding: 40px 20px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        text-align: center;
                    }}
                    .error-container {{
                        background: rgba(255, 255, 255, 0.1);
                        padding: 40px;
                        border-radius: 16px;
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(255, 255, 255, 0.2);
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                        max-width: 500px;
                    }}
                    h1 {{
                        margin: 0 0 20px 0;
                        font-size: 2.5em;
                        font-weight: 700;
                    }}
                    p {{
                        margin: 10px 0;
                        font-size: 1.1em;
                        line-height: 1.6;
                        opacity: 0.9;
                    }}
                    .error-details {{
                        background: rgba(255, 255, 255, 0.1);
                        padding: 20px;
                        border-radius: 8px;
                        margin-top: 20px;
                        font-family: monospace;
                        font-size: 0.9em;
                        text-align: left;
                    }}
                </style>
            </head>
            <body>
                <div class="error-container">
                    <h1> Clone Generator</h1>
                    <p>Unable to generate website clone due to an error in the AI processing.</p>
                    <p>Please try again with a different URL or check your API configuration.</p>
                    <div class="error-details">
                        <strong>Error:</strong> {str(e)}<br>
                        <strong>Type:</strong> {type(e).__name__}
                    </div>
                </div>
            </body>
            </html>"""
        
        logger.info("Returning enhanced fallback HTML due to error")
        return fallback_html