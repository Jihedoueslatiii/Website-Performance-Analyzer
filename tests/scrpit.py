from playwright.sync_api import Page

def test_load_homepage(page: Page):
    page.page.locator("#urlInput").fill("https://google.com")

    assert "Website Performance Analyzer" in page.content()
