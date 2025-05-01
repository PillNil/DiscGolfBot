import asyncio
from playwright.async_api import async_playwright
import re

class Hole:
    def __init__(self, hole, par):
        self.hole = hole
        self.par = par

class Answer:
    def __init__(self, site, holes_list):
        self.site = site
        self.holes_list = holes_list

async def query(search_term):
    async with async_playwright() as p:
        browser = await p.chromium.launch()  # Or firefox, webkit
        page = await browser.new_page()

        #search_term = input("What course are you playing today?")
        search_term_for_url = search_term.replace(" ", "+")
        await page.goto("https://udisc.com/courses?courseTerm=" + search_term_for_url)
        
        # Extract data 
        title = await page.title()
        content = await page.content()

        print(f"Title: {title}")

        course_list_header_element = await page.query_selector("h2:has-text('Disc golf courses')")
        # print(course_list_header_element)
        ul_element = await course_list_header_element.query_selector("xpath=following-sibling::*")
        # print(ul_element)
        first_course_element = await  ul_element.query_selector("li a")
        # print(first_course_element)
        end_of_url = await first_course_element.get_attribute("href")
        
        await page.goto("https://udisc.com" + end_of_url)
        
        layout_link = await page.locator("a", has_text="layouts").first.get_attribute("href")
        # print(layout_link)

        site_name = await page.locator("h1.text-xl.font-bold").first.inner_text()

        await page.goto("https://udisc.com" + layout_link)
        rows = page.locator("td.text-subtle.px-4.py-4.text-base")

        hole_data = []
        
        holes = page.locator("td.text-subtle.px-4.py-4.text-base:has-text('Hole')")
        for i in range(await holes.count()):
            hole_element = holes.nth(i)
            # print (hole_element.inner_text())
            next_tr_element = hole_element.locator("xpath=parent::tr//following-sibling::tr[1]")
            # print (next_tr_element)
            par_element = next_tr_element.locator("*:text('Par')")
            # print (par_element.inner_text())
            par_number = re.search(r"Par\s+(\d+)",await par_element.inner_text()).group(1)
            # print (re.search(r"Hole\s+(\d+)", par_element.inner_text()).group(1))
            hole_number = re.search(r"Hole\s+(\d+)", await hole_element.inner_text()).group(1)
            hole_data.append(Hole(int(hole_number), int(par_number)))

        answer_object = Answer(site_name, hole_data)

        return answer_object


async def example():
    search_term = input("What course do you want to play?")
    answer_object = await query(search_term)
    answer_text = f"At {answer_object.site}, the holes are:\n"
    for hole in answer_object.holes_list:
        answer_text += f"Hole {hole.hole} Par {hole.par}\n"
    print (answer_text)

if __name__ == "__main__":
    asyncio.run(example())
