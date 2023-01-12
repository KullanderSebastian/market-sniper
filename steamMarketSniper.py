from selenium import webdriver
import time
import re
import requests
import logging

driver = webdriver.Chrome()
urls = []

def sign_in():
    driver.get("https://steamcommunity.com/login/home/?goto=market%2Flistings%2F730")
    title = driver.title

    while title == "Sign In":
        print("Sign in to continue...")
        time.sleep(2.5)
        title = driver.title
    return True;

def get_skins():
    try:
        with open("skins.txt", "r", encoding="utf-8") as find_skin_values:
            for line in find_skin_values:
                if line.startswith("https://steamcommunity.com/market/listings/730/"):
                    urls.append(line)
                else:
                    continue
    except FileNotFoundError:
        print("Create a file named skins.txt and add the URLs for the skins you want to snipe.")
        driver.quit()

def get_user_input():
    url_info = [[0 for x in range(2)] for y in range(len(urls))]

    for x in range(len(urls)):
        while True:
            url_info[x][0] = float(input("Input float for skin number " + str(x + 1) + ": "))
            url_info[x][1] = float(input("Input max price for skin number " + str(x + 1) + ": "))
            break;

    print(url_info)
    return url_info

def load_buttons():
    inspect_button = driver.find_elements("class name", "market_actionmenu_button")
    buy_buttons = driver.find_elements("class name", "item_market_action_button")
    prices_box = driver.find_elements("xpath", "//span[@class='market_listing_price market_listing_price_with_fee']")
    return  inspect_button, buy_buttons, prices_box

def save_json_data(button):
    driver.execute_script("arguments[0].click();", button)
    popup = driver.find_element("css selector", "#market_action_popup_itemactions > a")
    href = popup.get_attribute("href")

    res = requests.get("https://api.csgofloat.com/?url=" + href)
    res.raise_for_status()
    json_res = res.json()
    json_res_name = str(json_res["iteminfo"]["full_item_name"])
    json_res_float = float(json_res["iteminfo"]["floatvalue"])
    json_res_pattern = int(json_res["iteminfo"]["paintseed"])

    print(json_res_name)
    print(json_res_float)

    return json_res_name, json_res_float, json_res_pattern, json_res

def next_page():
    try:
        print("Checking if next page exists...")
        next_page = driver.find_element("xpath", "//span[@id='searchResults_btn_next' and @class='pagebtn']")
        driver.execute_script("arguments[0].click();", next_page)
        time.sleep(2)
        return True
    except NoSuchElementException:
        print("There is no more pages.")
        return False

def check_max_price(order, price):
    if float(url_info_global[count][1]) >= float(price[order]):
        return True

    return False

def check_item_float_lower(item_float):
    if item_float < float(url_info_global[count][0]):
        return True

    return False

def check_skins():
    max_price_reached = False

    while True:
        buttons, buy_now, prices = load_buttons()

        price_text_number = []

        for price in prices:
            my_new_string = re.sub('[^.,a-zA-Z0-9 \n\.]', '', price.text)
            stripped_string = my_new_string.rstrip(",")
            stripped_string = stripped_string.replace(",", ".")
            price_text_number.append(stripped_string)

        for idx, btn in enumerate(buttons):
            if not check_max_price(idx, price_text_number):
                max_price_reached = True
                break

            skin_name, skin_float, skin_pattern, full_response = save_json_data(btn)

            if check_item_float_lower(skin_float):
                print("FOUND " + str(skin_name) + " WITH FLOAT: " + str(skin_float) + ".")
                logging.basicConfig(filename="items.log", encoding="utf-8", level=logging.INFO, format='%(asctime)s %(message)s')
                logging.info("Found " + str(skin_name) + " with float: " + str(skin_float) + ". Price: " + price_text_number[idx] + "EUR")

        if not next_page() or max_price_reached:
            break

sign_in()
get_skins()
url_info_global = get_user_input()
count = 0

while True:
    if count == len(urls):
        count = 0
    print("Searching url number:" + str(count + 1))
    driver.get(urls[count])
    check_skins()
    count += 1
