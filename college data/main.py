from playwright.sync_api import sync_playwright
import pandas as pd

def scrape_popup_data(college_id):
    data_list = []
    button_link = f"#ContentPlaceHolderMain_gvList_lnkViewDetails_{college_id}"
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch(headless=False)  # Set to True for headless mode
        page = browser.new_page()

        # Increase navigation timeout
        page.set_default_navigation_timeout(90000)  # 90 seconds global navigation timeout

        try:
            # Go to the college list page
            page.goto("https://admissions.highereduhry.ac.in/SearchCollege", wait_until="domcontentloaded", timeout=90000)

            # Wait until the button for the specified college ID is loaded
            page.wait_for_selector(button_link, timeout=60000)

            # Click the college link
            page.click(button_link)

            # Wait for the popup to load
            page.wait_for_selector(".modal-body .table.table-custom", timeout=60000)

            # Extract the table data after the popup is shown
            table = page.query_selector(".modal-body .table.table-custom")
            rows = table.query_selector_all("tr")

            # Iterate over table rows and extract cell data
            for row in rows[1:]:  # Skip the header row
                cells = row.query_selector_all("td")
                data_list.append([cell.inner_text().strip() for cell in cells])

            # Close the popup
            page.evaluate("document.querySelector('.modal .close').click()")

            # Wait for the popup to close and page to load
            page.wait_for_load_state("domcontentloaded")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Close the browser
            browser.close()

    return data_list

if __name__ == "__main__":
    all_data = []
    for college_id in range(345):  # Iterate through IDs from 0 to 344
        college_data = scrape_popup_data(college_id)
        all_data.extend(college_data)

    # Save the extracted data to a single CSV file
    columns = ["Column1", "Column2", "Column3", "Column4"]  # Adjust column names as needed
    df = pd.DataFrame(all_data, columns=columns)
    df.to_csv("popup_data.csv", index=False)
    
