from playwright.async_api import async_playwright


async def scrape_addgene_kit(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        my_page = await browser.new_page()
        # Change the URL to the site you want for your Playwright web scraping project
        await my_page.goto(url)
        await my_page.wait_for_load_state("load")

        # Error if #kit-contents-link is not found
        if not await my_page.query_selector("#kit-contents-link"):
            raise Exception(
                "Problem scraping AddGene website:'Kit contents' tab not found"
            )

        # Click on contents link
        await my_page.click("#kit-contents-link")
        await my_page.wait_for_load_state("load")

        # Error if the select element is not found
        if not await my_page.query_selector("label:has-text('Show ') >> select"):
            raise Exception("Problem scraping AddGene website: plasmid table not found")

        # Error if the option "All" is not found
        if not await my_page.query_selector(
            "label:has-text('Show ') >> select >> option[value='-1']"
        ):
            raise Exception(
                "Problem scraping AddGene website: option 'All' not found in the table of plasmids"
            )

        # Click on a select element inside a label
        # the label contains text "Show "
        # include label in the query
        # Select option "All"
        await my_page.select_option("label:has-text('Show ') >> select", "All")
        await my_page.wait_for_load_state("load")

        # Get content
        page_content = await my_page.content()

        # Close the browser
        await browser.close()

    return page_content


if __name__ == "__main__":
    import asyncio

    url = "https://www.addgene.org/kits/sieber-moclo-pichia-toolkit/"
    print(asyncio.run(scrape_addgene_kit(url)))
