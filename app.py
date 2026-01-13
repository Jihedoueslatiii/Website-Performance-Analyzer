from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from playwright.sync_api import sync_playwright
import time
import os
from urllib.parse import urlparse
import traceback

app = Flask(__name__)
CORS(app)

# Create screenshots directory if it doesn't exist
os.makedirs('static/screenshots', exist_ok=True)
CORS(app, 
    resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    }
)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_website():
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Validate URL
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return jsonify({'error': 'Invalid URL format'}), 400
        except Exception:
            return jsonify({'error': 'Invalid URL'}), 400
        
        results = run_analysis(url)
        return jsonify(results)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

def run_analysis(url):
    """Main analysis function using Playwright"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        metrics = {}
        issues = []
        detailed_breakdown = {
            'performance': [],
            'seo': [],
            'accessibility': [],
            'bestPractices': []
        }
        
        # Navigation timing
        start_time = time.time()
        
        try:
            response = page.goto(url, wait_until='domcontentloaded', timeout=30000)
            load_time = time.time() - start_time
            
            # Wait for page to settle
            page.wait_for_timeout(2000)
            
            # Take screenshot
            try:
                screenshot_path = f"static/screenshots/screenshot_{int(time.time())}.png"
                page.screenshot(path=screenshot_path, full_page=False)
                screenshot_url = f"/{screenshot_path}"
            except Exception as e:
                print(f"Screenshot error: {e}")
                screenshot_url = None
            
            # Get page title and description for confirmation
            try:
                page_info = page.evaluate("""() => {
                    return {
                        title: document.title,
                        description: document.querySelector('meta[name="description"]')?.content || '',
                        favicon: document.querySelector('link[rel*="icon"]')?.href || '',
                        h1: document.querySelector('h1')?.textContent?.trim() || 'No H1 found'
                    };
                }""")
            except:
                page_info = {
                    'title': 'Could not extract',
                    'description': 'Could not extract',
                    'favicon': '',
                    'h1': 'Could not extract'
                }
            
            # Get performance metrics
            try:
                performance_metrics = page.evaluate("""() => {
                    const perfData = window.performance.timing;
                    const paint = performance.getEntriesByType('paint');
                    
                    return {
                        dns: perfData.domainLookupEnd - perfData.domainLookupStart,
                        tcp: perfData.connectEnd - perfData.connectStart,
                        ttfb: perfData.responseStart - perfData.requestStart,
                        domLoad: perfData.domContentLoadedEventEnd - perfData.navigationStart,
                        pageLoad: perfData.loadEventEnd - perfData.navigationStart,
                        fcp: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0
                    };
                }""")
            except:
                performance_metrics = {
                    'dns': 0, 'tcp': 0, 'ttfb': 0,
                    'domLoad': load_time * 1000,
                    'pageLoad': load_time * 1000,
                    'fcp': 0
                }
            
            # Network requests count
            try:
                network_requests = page.evaluate("() => performance.getEntriesByType('resource').length")
            except:
                network_requests = 0
            
            # Page size
            try:
                page_content = page.content()
                page_size = len(page_content.encode('utf-8')) / 1024
            except:
                page_size = 0
            
            # Get CSS and JS file counts
            try:
                resource_breakdown = page.evaluate("""() => {
                    const resources = performance.getEntriesByType('resource');
                    return {
                        css: resources.filter(r => r.name.includes('.css')).length,
                        js: resources.filter(r => r.name.includes('.js')).length,
                        images: resources.filter(r => r.initiatorType === 'img').length,
                        fonts: resources.filter(r => r.name.includes('.woff') || r.name.includes('.ttf')).length
                    };
                }""")
            except:
                resource_breakdown = {'css': 0, 'js': 0, 'images': 0, 'fonts': 0}
            
            # Get detailed site overview
            try:
                site_overview = page.evaluate("""() => {
                    // Count elements
                    const allElements = document.getElementsByTagName('*').length;
                    const links = document.querySelectorAll('a').length;
                    const internalLinks = Array.from(document.querySelectorAll('a')).filter(a => 
                        a.href.startsWith(window.location.origin) || a.href.startsWith('/')
                    ).length;
                    const externalLinks = links - internalLinks;
                    const forms = document.querySelectorAll('form').length;
                    const buttons = document.querySelectorAll('button, input[type="submit"]').length;
                    const headings = {
                        h1: document.querySelectorAll('h1').length,
                        h2: document.querySelectorAll('h2').length,
                        h3: document.querySelectorAll('h3').length,
                        h4: document.querySelectorAll('h4').length,
                        h5: document.querySelectorAll('h5').length,
                        h6: document.querySelectorAll('h6').length
                    };
                    
                    // Get all meta tags
                    const metaTags = Array.from(document.querySelectorAll('meta')).map(meta => ({
                        name: meta.name || meta.property || 'http-equiv',
                        content: meta.content ? meta.content.substring(0, 100) : ''
                    }));
                    
                    // Get language
                    const lang = document.documentElement.lang || 'not specified';
                    
                    // Get character encoding
                    const charset = document.characterSet || 'not specified';
                    
                    // Get all CSS files
                    const cssFiles = Array.from(document.querySelectorAll('link[rel="stylesheet"]')).map(link => ({
                        href: link.href,
                        media: link.media || 'all'
                    }));
                    
                    // Get all JS files
                    const jsFiles = Array.from(document.querySelectorAll('script[src]')).map(script => ({
                        src: script.src,
                        async: script.async,
                        defer: script.defer
                    }));
                    
                    // Get inline scripts count
                    const inlineScripts = document.querySelectorAll('script:not([src])').length;
                    
                    // Get favicon
                    const favicon = document.querySelector('link[rel*="icon"]')?.href || 'none';
                    
                    // Get schema.org markup
                    const schemaMarkup = document.querySelectorAll('script[type="application/ld+json"]').length;
                    
                    // Get Open Graph tags
                    const ogTags = Array.from(document.querySelectorAll('meta[property^="og:"]')).map(meta => ({
                        property: meta.property,
                        content: meta.content
                    }));
                    
                    // Get Twitter Card tags
                    const twitterTags = Array.from(document.querySelectorAll('meta[name^="twitter:"]')).map(meta => ({
                        name: meta.name,
                        content: meta.content
                    }));
                    
                    // Get all images with details
                    const images = Array.from(document.querySelectorAll('img')).map(img => ({
                        src: img.src,
                        alt: img.alt || 'missing',
                        width: img.width || 'auto',
                        height: img.height || 'auto',
                        loading: img.loading || 'eager'
                    }));
                    
                    // Check for lazy loading
                    const lazyLoadedImages = images.filter(img => img.loading === 'lazy').length;
                    
                    return {
                        totalElements: allElements,
                        links: { total: links, internal: internalLinks, external: externalLinks },
                        forms: forms,
                        buttons: buttons,
                        headings: headings,
                        metaTags: metaTags,
                        language: lang,
                        charset: charset,
                        cssFiles: cssFiles,
                        jsFiles: jsFiles,
                        inlineScripts: inlineScripts,
                        favicon: favicon,
                        schemaMarkup: schemaMarkup,
                        ogTags: ogTags,
                        twitterTags: twitterTags,
                        images: images,
                        lazyLoadedImages: lazyLoadedImages
                    };
                }""")
            except Exception as e:
                print(f"Error getting site overview: {e}")
                site_overview = {
                    'totalElements': 0,
                    'links': {'total': 0, 'internal': 0, 'external': 0},
                    'forms': 0,
                    'buttons': 0,
                    'headings': {'h1': 0, 'h2': 0, 'h3': 0, 'h4': 0, 'h5': 0, 'h6': 0},
                    'metaTags': [],
                    'language': 'not detected',
                    'charset': 'not detected',
                    'cssFiles': [],
                    'jsFiles': [],
                    'inlineScripts': 0,
                    'favicon': 'none',
                    'schemaMarkup': 0,
                    'ogTags': [],
                    'twitterTags': [],
                    'images': [],
                    'lazyLoadedImages': 0
                }
            
            metrics = {
                'ttfb': f"{performance_metrics.get('ttfb', 0):.0f}ms",
                'fcp': f"{performance_metrics.get('fcp', 0):.0f}ms",
                'domLoad': f"{performance_metrics.get('domLoad', 0):.0f}ms",
                'pageLoad': f"{performance_metrics.get('pageLoad', 0):.0f}ms",
                'networkRequests': network_requests,
                'pageSize': f"{page_size:.2f} KB",
                'loadTime': f"{load_time:.2f}s",
                'cssFiles': resource_breakdown['css'],
                'jsFiles': resource_breakdown['js'],
                'imageCount': resource_breakdown['images'],
                'fontFiles': resource_breakdown['fonts']
            }
            
            # Check HTTPS
            is_https = url.startswith('https://')
            if not is_https:
                issues.append({
                    'title': 'Not using HTTPS',
                    'description': 'Website is not secured with HTTPS encryption',
                    'severity': 'error',
                    'impact': 'High security risk, affects SEO ranking'
                })
                detailed_breakdown['seo'].append({
                    'check': 'HTTPS',
                    'status': 'fail',
                    'points_lost': 15,
                    'reason': 'Not using HTTPS protocol'
                })
                detailed_breakdown['bestPractices'].append({
                    'check': 'HTTPS',
                    'status': 'fail',
                    'points_lost': 30,
                    'reason': 'No SSL/TLS encryption'
                })
            else:
                issues.append({
                    'title': 'Using HTTPS',
                    'description': 'Website is properly secured with HTTPS',
                    'severity': 'success',
                    'impact': 'Secure connection established'
                })
                detailed_breakdown['seo'].append({
                    'check': 'HTTPS',
                    'status': 'pass',
                    'points_lost': 0,
                    'reason': 'Properly secured'
                })
            
            # Check for missing alt tags
            try:
                alt_data = page.evaluate("""() => {
                    const imgs = document.querySelectorAll('img');
                    const total = imgs.length;
                    const missing = Array.from(imgs).filter(img => !img.alt).length;
                    return {total, missing};
                }""")
                total_images = alt_data['total']
                missing_alts = alt_data['missing']
            except:
                total_images = 0
                missing_alts = 0
            
            if missing_alts > 0:
                percentage = (missing_alts / total_images * 100) if total_images > 0 else 0
                issues.append({
                    'title': f'Missing Alt Tags on {missing_alts}/{total_images} Images',
                    'description': f'{percentage:.1f}% of images lack alt attributes for screen readers',
                    'severity': 'warning',
                    'impact': f'Affects {missing_alts} images - reduces accessibility score'
                })
                points_lost = min(missing_alts * 5, 40)
                detailed_breakdown['accessibility'].append({
                    'check': 'Image Alt Attributes',
                    'status': 'fail',
                    'points_lost': points_lost,
                    'reason': f'{missing_alts} images missing alt text ({percentage:.1f}%)'
                })
            else:
                if total_images > 0:
                    issues.append({
                        'title': f'All {total_images} Images Have Alt Tags',
                        'description': 'All images properly labeled for accessibility',
                        'severity': 'success',
                        'impact': 'Screen reader friendly'
                    })
            
            # Check SEO meta tags
            try:
                meta_checks = page.evaluate("""() => {
                    const title = document.title;
                    const description = document.querySelector('meta[name="description"]')?.content || '';
                    return {
                        title: title,
                        titleLength: title.length,
                        description: description,
                        descriptionLength: description.length,
                        viewport: !!document.querySelector('meta[name="viewport"]'),
                        ogImage: !!document.querySelector('meta[property="og:image"]'),
                        ogTitle: !!document.querySelector('meta[property="og:title"]'),
                        ogDescription: !!document.querySelector('meta[property="og:description"]'),
                        canonical: !!document.querySelector('link[rel="canonical"]'),
                        robots: document.querySelector('meta[name="robots"]')?.content || 'not set'
                    };
                }""")
            except:
                meta_checks = {
                    'title': '',
                    'titleLength': 0,
                    'description': '',
                    'descriptionLength': 0,
                    'viewport': False,
                    'ogImage': False,
                    'ogTitle': False,
                    'ogDescription': False,
                    'canonical': False,
                    'robots': 'not set'
                }
            
            # Title checks
            if meta_checks['titleLength'] == 0:
                issues.append({
                    'title': 'Missing Page Title',
                    'description': 'No title tag found',
                    'severity': 'error',
                    'impact': 'Critical SEO issue - 30 points lost'
                })
                detailed_breakdown['seo'].append({
                    'check': 'Title Tag',
                    'status': 'fail',
                    'points_lost': 30,
                    'reason': 'Title tag is completely missing'
                })
            elif meta_checks['titleLength'] < 30:
                issues.append({
                    'title': 'Title Too Short',
                    'description': f'Title is {meta_checks["titleLength"]} characters. Recommended: 50-60',
                    'severity': 'warning',
                    'impact': '10 points lost - title should be 50-60 characters'
                })
                detailed_breakdown['seo'].append({
                    'check': 'Title Length',
                    'status': 'warning',
                    'points_lost': 10,
                    'reason': f'Only {meta_checks["titleLength"]} characters (optimal: 50-60)'
                })
            elif meta_checks['titleLength'] > 60:
                issues.append({
                    'title': 'Title Too Long',
                    'description': f'Title is {meta_checks["titleLength"]} characters. Recommended: 50-60',
                    'severity': 'warning',
                    'impact': f'{meta_checks["titleLength"] - 60} characters will be truncated in search results'
                })
                detailed_breakdown['seo'].append({
                    'check': 'Title Length',
                    'status': 'warning',
                    'points_lost': 10,
                    'reason': f'{meta_checks["titleLength"]} characters (optimal: 50-60)'
                })
            else:
                issues.append({
                    'title': 'Title Length Optimal',
                    'description': f'Title is {meta_checks["titleLength"]} characters - perfect length',
                    'severity': 'success',
                    'impact': 'Well optimized for search results'
                })
            
            # Description checks
            if meta_checks['descriptionLength'] == 0:
                issues.append({
                    'title': 'Missing Meta Description',
                    'description': 'No meta description tag found',
                    'severity': 'error',
                    'impact': 'Critical SEO issue - 25 points lost'
                })
                detailed_breakdown['seo'].append({
                    'check': 'Meta Description',
                    'status': 'fail',
                    'points_lost': 25,
                    'reason': 'Meta description is completely missing'
                })
            elif meta_checks['descriptionLength'] < 120:
                issues.append({
                    'title': 'Meta Description Too Short',
                    'description': f'Description is {meta_checks["descriptionLength"]} characters. Recommended: 150-160',
                    'severity': 'warning',
                    'impact': 'Could provide more detail for search results'
                })
            elif meta_checks['descriptionLength'] > 160:
                issues.append({
                    'title': 'Meta Description Too Long',
                    'description': f'Description is {meta_checks["descriptionLength"]} characters. Recommended: 150-160',
                    'severity': 'warning',
                    'impact': f'{meta_checks["descriptionLength"] - 160} characters will be truncated'
                })
            else:
                issues.append({
                    'title': 'Meta Description Optimal',
                    'description': f'Description is {meta_checks["descriptionLength"]} characters - perfect length',
                    'severity': 'success',
                    'impact': 'Well optimized for search results'
                })
            
            # Viewport check
            if not meta_checks['viewport']:
                issues.append({
                    'title': 'Missing Viewport Meta Tag',
                    'description': 'No viewport meta tag for mobile responsiveness',
                    'severity': 'error',
                    'impact': '10 points lost from SEO, 15 from accessibility'
                })
                detailed_breakdown['seo'].append({
                    'check': 'Viewport Meta Tag',
                    'status': 'fail',
                    'points_lost': 10,
                    'reason': 'Mobile viewport not configured'
                })
                detailed_breakdown['accessibility'].append({
                    'check': 'Mobile Viewport',
                    'status': 'fail',
                    'points_lost': 15,
                    'reason': 'Not mobile-friendly'
                })
            
            # Open Graph checks
            if not meta_checks['ogImage']:
                detailed_breakdown['seo'].append({
                    'check': 'Open Graph Image',
                    'status': 'fail',
                    'points_lost': 10,
                    'reason': 'No og:image for social sharing'
                })
            
            # Performance breakdown
            ttfb = performance_metrics.get('ttfb', 0)
            fcp = performance_metrics.get('fcp', 0)
            page_load = performance_metrics.get('pageLoad', 0)
            
            # TTFB analysis
            if ttfb > 600:
                points = 10
                issues.append({
                    'title': f'Slow Server Response: {ttfb:.0f}ms',
                    'description': f'TTFB is {ttfb - 600:.0f}ms slower than recommended (600ms)',
                    'severity': 'warning',
                    'impact': f'Server response time costs {points} performance points'
                })
                detailed_breakdown['performance'].append({
                    'check': 'Time to First Byte (TTFB)',
                    'status': 'fail',
                    'points_lost': points,
                    'reason': f'{ttfb:.0f}ms (optimal: <600ms, {ttfb - 600:.0f}ms too slow)'
                })
            else:
                detailed_breakdown['performance'].append({
                    'check': 'Time to First Byte (TTFB)',
                    'status': 'pass',
                    'points_lost': 0,
                    'reason': f'{ttfb:.0f}ms (optimal: <600ms)'
                })
            
            # FCP analysis
            if fcp > 2000:
                points = 15
                issues.append({
                    'title': f'Slow First Contentful Paint: {fcp:.0f}ms',
                    'description': f'FCP is {fcp - 2000:.0f}ms slower than recommended (2000ms)',
                    'severity': 'warning',
                    'impact': f'Content appears {points} points too slowly'
                })
                detailed_breakdown['performance'].append({
                    'check': 'First Contentful Paint (FCP)',
                    'status': 'fail',
                    'points_lost': points,
                    'reason': f'{fcp:.0f}ms (optimal: <2000ms, {fcp - 2000:.0f}ms too slow)'
                })
            else:
                detailed_breakdown['performance'].append({
                    'check': 'First Contentful Paint (FCP)',
                    'status': 'pass',
                    'points_lost': 0,
                    'reason': f'{fcp:.0f}ms (optimal: <2000ms)'
                })
            
            # Page Load analysis
            if page_load > 3000:
                points = 20
                issues.append({
                    'title': f'Slow Page Load: {page_load:.0f}ms',
                    'description': f'Page takes {page_load - 3000:.0f}ms longer than recommended (3000ms)',
                    'severity': 'warning',
                    'impact': f'Total load time costs {points} performance points'
                })
                detailed_breakdown['performance'].append({
                    'check': 'Total Page Load',
                    'status': 'fail',
                    'points_lost': points,
                    'reason': f'{page_load:.0f}ms (optimal: <3000ms, {page_load - 3000:.0f}ms too slow)'
                })
            else:
                detailed_breakdown['performance'].append({
                    'check': 'Total Page Load',
                    'status': 'pass',
                    'points_lost': 0,
                    'reason': f'{page_load:.0f}ms (optimal: <3000ms)'
                })
            
            # Network requests analysis
            if network_requests > 50:
                points = 15
                issues.append({
                    'title': f'Too Many Network Requests: {network_requests}',
                    'description': f'{network_requests - 50} more requests than recommended (50 max)',
                    'severity': 'warning',
                    'impact': f'Excessive requests cost {points} performance points'
                })
                detailed_breakdown['performance'].append({
                    'check': 'Network Requests',
                    'status': 'fail',
                    'points_lost': points,
                    'reason': f'{network_requests} requests (optimal: <50, {network_requests - 50} excess)'
                })
                detailed_breakdown['bestPractices'].append({
                    'check': 'Resource Optimization',
                    'status': 'fail',
                    'points_lost': 10,
                    'reason': f'{network_requests} requests - should bundle/minimize'
                })
            else:
                detailed_breakdown['performance'].append({
                    'check': 'Network Requests',
                    'status': 'pass',
                    'points_lost': 0,
                    'reason': f'{network_requests} requests (optimal: <50)'
                })
            
            # Page size analysis
            if page_size > 1000:
                points = 10
                issues.append({
                    'title': f'Large Page Size: {page_size:.2f} KB',
                    'description': f'Page is {page_size - 1000:.2f} KB larger than recommended (1000 KB)',
                    'severity': 'warning',
                    'impact': f'Page size costs {points} performance points'
                })
                detailed_breakdown['performance'].append({
                    'check': 'Page Size',
                    'status': 'fail',
                    'points_lost': points,
                    'reason': f'{page_size:.0f}KB (optimal: <1000KB, {page_size - 1000:.0f}KB too large)'
                })
                detailed_breakdown['bestPractices'].append({
                    'check': 'Page Weight',
                    'status': 'fail',
                    'points_lost': 10,
                    'reason': f'{page_size:.0f}KB - compress assets'
                })
            else:
                detailed_breakdown['performance'].append({
                    'check': 'Page Size',
                    'status': 'pass',
                    'points_lost': 0,
                    'reason': f'{page_size:.0f}KB (optimal: <1000KB)'
                })
            
            # Calculate scores with detailed breakdown
            scores = calculate_scores(
                performance_metrics, 
                network_requests, 
                page_size, 
                is_https, 
                missing_alts, 
                meta_checks,
                detailed_breakdown
            )
            
        except Exception as e:
            browser.close()
            raise Exception(f"Failed to load or analyze page: {str(e)}")
        
        browser.close()
        
        return {
            'url': url,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'pageInfo': page_info,
            'screenshot': screenshot_url,
            'scores': scores,
            'metrics': metrics,
            'issues': issues,
            'breakdown': detailed_breakdown,
            'overview': site_overview
        }

def calculate_scores(perf_metrics, network_reqs, page_size, is_https, missing_alts, meta_checks, breakdown):
    """Calculate precise scores for each category (0-100)"""
    
    # Performance Score (starts at 100)
    perf_score = 100
    for item in breakdown['performance']:
        perf_score -= item['points_lost']
    perf_score = max(0, perf_score)
    
    # SEO Score (starts at 100)
    seo_score = 100
    for item in breakdown['seo']:
        seo_score -= item['points_lost']
    seo_score = max(0, seo_score)
    
    # Accessibility Score (starts at 100)
    access_score = 100
    for item in breakdown['accessibility']:
        access_score -= item['points_lost']
    access_score = max(0, access_score)
    
    # Best Practices Score (starts at 100)
    bp_score = 100
    for item in breakdown['bestPractices']:
        bp_score -= item['points_lost']
    bp_score = max(0, bp_score)
    
    return {
        'performance': perf_score,
        'seo': seo_score,
        'accessibility': access_score,
        'bestPractices': bp_score
    }

if __name__ == '__main__':
    print("🚀 Website Analyzer Starting...")
    print("📁 Make sure index.html is in templates/ folder")
    print("🌐 Server: http://localhost:5000")
    app.run(debug=True, port=5000)