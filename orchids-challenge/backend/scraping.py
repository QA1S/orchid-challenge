from playwright.async_api import async_playwright
import re
import asyncio
from typing import Dict, List, Optional
import logging
import base64

logger = logging.getLogger(__name__)

async def scrape_website(url: str) -> str:
    """
    Enhanced scraping to capture comprehensive visual design information
    """
    logger.info(f"Starting scraping for URL: {url}")
    
    async with async_playwright() as p:
        browser = None
        try:
            logger.info("Launching browser...")
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-extensions',
                    '--disable-plugins',
                    # Don't disable images - we need them for visual analysis
                ]
            )
            page = await browser.new_page()
            
            # Set a reasonable viewport size
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Set user agent to avoid bot detection
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            logger.info(f"Navigating to {url}...")
            
            # Try multiple wait strategies with increasing timeouts
            html = None
            title = None
            
            try:
                # First attempt: Wait for domcontentloaded (faster)
                logger.info("Attempting with domcontentloaded...")
                await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                await page.wait_for_timeout(5000)  # Increased wait for dynamic content
                html = await page.content()
                title = await page.title()
                logger.info("Successfully loaded with domcontentloaded")
                
            except Exception as e1:
                logger.warning(f"domcontentloaded failed: {str(e1)}")
                try:
                    # Second attempt: Wait for load event
                    logger.info("Attempting with load event...")
                    await page.goto(url, timeout=45000, wait_until="load")
                    await page.wait_for_timeout(3000)
                    html = await page.content()
                    title = await page.title()
                    logger.info("Successfully loaded with load event")
                    
                except Exception as e2:
                    logger.warning(f"load event failed: {str(e2)}")
                    try:
                        # Third attempt: Just navigate without waiting
                        logger.info("Attempting basic navigation...")
                        await page.goto(url, timeout=60000)
                        await page.wait_for_timeout(8000)  # Give it more time
                        html = await page.content()
                        title = await page.title()
                        logger.info("Successfully loaded with basic navigation")
                        
                    except Exception as e3:
                        logger.error(f"All navigation attempts failed: {str(e3)}")
                        raise Exception(f"Failed to load page after multiple attempts: {str(e3)}")
            
            if not html:
                raise Exception("Failed to retrieve HTML content")
                
            logger.info(f"Page title: {title}")
            logger.info(f"HTML content length: {len(html)} characters")
            
            # Extract comprehensive design information
            logger.info("Extracting comprehensive design context...")
            design_info = await extract_comprehensive_design_context(page)
            
            # Take a screenshot for additional context
            logger.info("Taking screenshot for visual reference...")
            screenshot_data = await take_screenshot(page)
            
            # Get text content for understanding the site's purpose
            logger.info("Extracting text content...")
            try:
                text_content = await page.evaluate("""
                    () => {
                        // Remove script and style elements
                        const scripts = document.querySelectorAll('script, style');
                        scripts.forEach(el => el.remove());
                        
                        // Get visible text content
                        const text = document.body.innerText || document.body.textContent || '';
                        return text.slice(0, 2000);  // Increased limit
                    }
                """)
            except Exception as e:
                logger.warning(f"Failed to extract text content: {str(e)}")
                text_content = "Unable to extract text content"
                
            logger.info(f"Text content length: {len(text_content)} characters")

            await browser.close()
            logger.info("Browser closed")
            
            # Compile comprehensive context with better formatting
            context = f"""
                        WEBSITE ANALYSIS REPORT
                        ======================
                        URL: {url}
                        Title: {title}

                        VISUAL DESIGN ANALYSIS:
                        {design_info}

                        SCREENSHOT CONTEXT:
                        {screenshot_data}

                        CONTENT OVERVIEW:
                        {text_content[:800]}...

                        HTML STRUCTURE FOR REFERENCE:
                        {clean_html_structure(html[:3000])}...

                        STYLING CONTEXT:
                        {extract_css_from_html(html[:5000])}
                        """
            logger.info(f"Context compiled. Total length: {len(context)} characters")
            # return context.strip()
            return {
                "context": context.strip(),          # your big text report
                "screenshot": screenshot_data    # raw image
            }
            
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            if browser:
                try:
                    await browser.close()
                except:
                    pass
            raise Exception(f"Failed to scrape website: {str(e)}")


async def extract_comprehensive_design_context(page) -> str:
    """
    Extract comprehensive design information including colors, layout, typography, and visual elements
    """
    try:
        logger.info("Extracting comprehensive design context...")
        
        # Add timeout to prevent hanging
        design_info = await asyncio.wait_for(
            page.evaluate("""
                () => {
                    const info = {};
                    
                    try {
                        // Get root/body styles
                        const body = document.body;
                        const html = document.documentElement;
                        const bodyStyle = window.getComputedStyle(body);
                        const htmlStyle = window.getComputedStyle(html);
                        
                        // Background information
                        info.bodyBackground = {
                            backgroundColor: bodyStyle.backgroundColor,
                            backgroundImage: bodyStyle.backgroundImage,
                            backgroundSize: bodyStyle.backgroundSize,
                            backgroundPosition: bodyStyle.backgroundPosition,
                            backgroundRepeat: bodyStyle.backgroundRepeat
                        };
                        
                        info.htmlBackground = {
                            backgroundColor: htmlStyle.backgroundColor,
                            backgroundImage: htmlStyle.backgroundImage
                        };
                        
                        // Typography
                        info.typography = {
                            fontFamily: bodyStyle.fontFamily,
                            fontSize: bodyStyle.fontSize,
                            lineHeight: bodyStyle.lineHeight,
                            fontWeight: bodyStyle.fontWeight,
                            color: bodyStyle.color
                        };
                        
                        // Get all unique colors used on the page
                        const colors = new Set();
                        const backgrounds = new Set();
                        const elements = document.querySelectorAll('*');
                        
                        // Sample more elements but with better filtering
                        const sampleSize = Math.min(elements.length, 100);
                        for (let i = 0; i < sampleSize; i++) {
                            try {
                                const style = window.getComputedStyle(elements[i]);
                                
                                // Collect background colors
                                if (style.backgroundColor && style.backgroundColor !== 'rgba(0, 0, 0, 0)' && style.backgroundColor !== 'transparent') {
                                    backgrounds.add(style.backgroundColor);
                                }
                                
                                // Collect text colors
                                if (style.color && style.color !== 'rgba(0, 0, 0, 0)') {
                                    colors.add(style.color);
                                }
                                
                                // Collect border colors
                                if (style.borderColor && style.borderColor !== 'rgba(0, 0, 0, 0)') {
                                    colors.add(style.borderColor);
                                }
                            } catch (e) {
                                continue;
                            }
                        }
                        
                        info.colorPalette = {
                            backgrounds: Array.from(backgrounds).slice(0, 10),
                            textColors: Array.from(colors).slice(0, 10)
                        };
                        
                        // Layout analysis
                        const header = document.querySelector('header, .header, nav, .nav, [role="banner"]');
                        const main = document.querySelector('main, .main, .content, [role="main"]');
                        const footer = document.querySelector('footer, .footer, [role="contentinfo"]');
                        
                        info.layout = {
                            hasHeader: !!header,
                            hasMain: !!main,
                            hasFooter: !!footer,
                            headerHeight: header ? header.offsetHeight : 0,
                            mainHeight: main ? main.offsetHeight : 0
                        };
                        
                        // Get prominent headings with their styles
                        const headings = Array.from(document.querySelectorAll('h1, h2, h3')).slice(0, 5);
                        info.headings = headings.map(h => {
                            const style = window.getComputedStyle(h);
                            return {
                                tag: h.tagName,
                                text: (h.textContent || '').trim().slice(0, 100),
                                fontSize: style.fontSize,
                                fontWeight: style.fontWeight,
                                color: style.color,
                                textAlign: style.textAlign
                            };
                        });
                        
                        // Check for gradients and special effects
                        info.visualEffects = {
                            hasGradients: false,
                            gradientElements: [],
                            hasShadows: false,
                            shadowElements: []
                        };
                        
                        // Look for gradients
                        const gradientElements = Array.from(document.querySelectorAll('*')).filter(el => {
                            const style = window.getComputedStyle(el);
                            return style.backgroundImage && style.backgroundImage.includes('gradient');
                        }).slice(0, 5);
                        
                        if (gradientElements.length > 0) {
                            info.visualEffects.hasGradients = true;
                            info.visualEffects.gradientElements = gradientElements.map(el => {
                                const style = window.getComputedStyle(el);
                                return {
                                    tagName: el.tagName,
                                    className: el.className,
                                    backgroundImage: style.backgroundImage
                                };
                            });
                        }
                        
                        // Look for box shadows
                        const shadowElements = Array.from(document.querySelectorAll('*')).filter(el => {
                            const style = window.getComputedStyle(el);
                            return style.boxShadow && style.boxShadow !== 'none';
                        }).slice(0, 5);
                        
                        if (shadowElements.length > 0) {
                            info.visualEffects.hasShadows = true;
                            info.visualEffects.shadowElements = shadowElements.map(el => {
                                const style = window.getComputedStyle(el);
                                return {
                                    tagName: el.tagName,
                                    className: el.className,
                                    boxShadow: style.boxShadow
                                };
                            });
                        }
                        
                        // UI Components
                        info.components = {
                            hasNavigation: !!document.querySelector('nav, .navigation, .menu'),
                            hasButtons: document.querySelectorAll('button, .button, .btn, [role="button"]').length,
                            hasCards: document.querySelectorAll('.card, .box, .item, .tile').length,
                            hasGrid: document.querySelectorAll('.grid, .row, .columns, .flex').length,
                            hasHero: !!document.querySelector('.hero, .banner, .jumbotron, .hero-section'),
                            hasModal: !!document.querySelector('.modal, .popup, .overlay'),
                            hasCarousel: !!document.querySelector('.carousel, .slider, .swiper')
                        };
                        
                        // Get button styles
                        const buttons = Array.from(document.querySelectorAll('button, .button, .btn')).slice(0, 3);
                        info.buttonStyles = buttons.map(btn => {
                            const style = window.getComputedStyle(btn);
                            return {
                                backgroundColor: style.backgroundColor,
                                color: style.color,
                                borderRadius: style.borderRadius,
                                padding: style.padding,
                                fontSize: style.fontSize,
                                fontWeight: style.fontWeight,
                                border: style.border,
                                textContent: btn.textContent.trim().slice(0, 50)
                            };
                        });
                        
                        return info;
                    } catch (e) {
                        return { error: e.message };
                    }
                }
            """),
            timeout=15.0
        )
        
        logger.info("Comprehensive design context extraction completed")
        
        # Check if there was an error in the extraction
        if 'error' in design_info:
            logger.warning(f"Error in design extraction: {design_info['error']}")
            return f"Partial design context extracted. Error: {design_info['error']}"
        
        # Format the comprehensive design information
        formatted_info = f"""
BACKGROUND & COLORS:
- Body Background: {design_info.get('bodyBackground', {}).get('backgroundColor', 'N/A')}
- Body Background Image: {design_info.get('bodyBackground', {}).get('backgroundImage', 'N/A')[:100]}...
- HTML Background: {design_info.get('htmlBackground', {}).get('backgroundColor', 'N/A')}
- Background Colors Found: {', '.join(design_info.get('colorPalette', {}).get('backgrounds', [])[:5])}
- Text Colors Found: {', '.join(design_info.get('colorPalette', {}).get('textColors', [])[:5])}

TYPOGRAPHY:
- Font Family: {design_info.get('typography', {}).get('fontFamily', 'N/A')}
- Font Size: {design_info.get('typography', {}).get('fontSize', 'N/A')}
- Font Weight: {design_info.get('typography', {}).get('fontWeight', 'N/A')}
- Text Color: {design_info.get('typography', {}).get('color', 'N/A')}
- Line Height: {design_info.get('typography', {}).get('lineHeight', 'N/A')}

LAYOUT STRUCTURE:
- Has Header: {design_info.get('layout', {}).get('hasHeader', False)}
- Has Main: {design_info.get('layout', {}).get('hasMain', False)}
- Has Footer: {design_info.get('layout', {}).get('hasFooter', False)}
- Header Height: {design_info.get('layout', {}).get('headerHeight', 0)}px

VISUAL EFFECTS:
- Has Gradients: {design_info.get('visualEffects', {}).get('hasGradients', False)}
- Gradient Details: {format_gradients(design_info.get('visualEffects', {}).get('gradientElements', []))}
- Has Shadows: {design_info.get('visualEffects', {}).get('hasShadows', False)}
- Shadow Details: {format_shadows(design_info.get('visualEffects', {}).get('shadowElements', []))}

UI COMPONENTS:
- Navigation: {design_info.get('components', {}).get('hasNavigation', False)}
- Buttons Count: {design_info.get('components', {}).get('hasButtons', 0)}
- Cards Count: {design_info.get('components', {}).get('hasCards', 0)}
- Has Hero Section: {design_info.get('components', {}).get('hasHero', False)}
- Has Grid Layout: {design_info.get('components', {}).get('hasGrid', 0) > 0}

BUTTON STYLES:
{format_button_styles(design_info.get('buttonStyles', []))}

CONTENT HEADINGS:
{format_detailed_headings(design_info.get('headings', []))}
"""
        return formatted_info
        
    except asyncio.TimeoutError:
        logger.error("Timeout while extracting comprehensive design context")
        return "Could not extract design context: Operation timed out"
    except Exception as e:
        logger.error(f"Error extracting comprehensive design context: {str(e)}")
        return f"Could not extract design context: {str(e)}"


async def take_screenshot(page) -> str:
    """
    Capture a PNG screenshot and return raw base64 (no wrapping text).
    """
    screenshot = await page.screenshot(full_page=True, type="png")
    return base64.b64encode(screenshot).decode() 


def format_gradients(gradient_elements: List[Dict]) -> str:
    """Format gradient information"""
    if not gradient_elements:
        return "None found"
    
    formatted = []
    for elem in gradient_elements:
        formatted.append(f"  - {elem.get('tagName', 'Unknown')}.{elem.get('className', 'no-class')}: {elem.get('backgroundImage', '')[:100]}...")
    
    return '\n' + '\n'.join(formatted) if formatted else "None found"


def format_shadows(shadow_elements: List[Dict]) -> str:
    """Format shadow information"""
    if not shadow_elements:
        return "None found"
    
    formatted = []
    for elem in shadow_elements:
        formatted.append(f"  - {elem.get('tagName', 'Unknown')}.{elem.get('className', 'no-class')}: {elem.get('boxShadow', '')}")
    
    return '\n' + '\n'.join(formatted) if formatted else "None found"


def format_button_styles(button_styles: List[Dict]) -> str:
    """Format button style information"""
    if not button_styles:
        return "- No buttons found"
    
    formatted = []
    for i, btn in enumerate(button_styles):
        formatted.append(f"""
Button {i+1} ("{btn.get('textContent', 'No text')[:30]}..."):
  - Background: {btn.get('backgroundColor', 'N/A')}
  - Color: {btn.get('color', 'N/A')}
  - Border Radius: {btn.get('borderRadius', 'N/A')}
  - Padding: {btn.get('padding', 'N/A')}
  - Font Weight: {btn.get('fontWeight', 'N/A')}
  - Border: {btn.get('border', 'N/A')}""")
    
    return '\n'.join(formatted)


def format_detailed_headings(headings: List[Dict]) -> str:
    """Format detailed heading information"""
    if not headings:
        return "- No major headings found"
    
    formatted = []
    for heading in headings:
        formatted.append(f"""
{heading.get('tag', 'Unknown')}: "{heading.get('text', 'No text')[:50]}..."
  - Font Size: {heading.get('fontSize', 'N/A')}
  - Font Weight: {heading.get('fontWeight', 'N/A')}
  - Color: {heading.get('color', 'N/A')}
  - Text Align: {heading.get('textAlign', 'N/A')}""")
    
    return '\n'.join(formatted)


def clean_html_structure(html: str) -> str:
    """Clean HTML but preserve more structure for better context"""
    # Remove scripts and styles content but keep tags
    html = re.sub(r'<script[^>]*>.*?</script>', '<script></script>', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '<style></style>', html, flags=re.DOTALL)
    
    # Keep the structure but remove excessive content
    return html


def extract_css_from_html(html: str) -> str:
    """Extract CSS styles from HTML for better context"""
    try:
        # Find style tags
        style_matches = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL)
        
        # Find inline styles
        inline_styles = re.findall(r'style="([^"]*)"', html)
        
        css_context = ""
        
        if style_matches:
            css_context += "EMBEDDED CSS STYLES:\n"
            for i, style in enumerate(style_matches[:2]):  # Limit to first 2 style blocks
                css_context += f"Style Block {i+1}:\n{style[:500]}...\n\n"
        
        if inline_styles:
            css_context += "INLINE STYLES SAMPLE:\n"
            for style in inline_styles[:5]:  # Limit to first 5 inline styles
                css_context += f"- {style}\n"
        
        return css_context if css_context else "No CSS styles found in HTML"
        
    except Exception as e:
        logger.warning(f"Failed to extract CSS: {str(e)}")
        return "CSS extraction failed"