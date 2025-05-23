import tkinter as tk
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import ddddocr
from PIL import Image

# 初始化 OCR（原本的設定）
ocr = ddddocr.DdddOcr()

def take_canvas_screenshot(driver, canvas_id, file_name):
    canvas = driver.find_element(By.ID, canvas_id)
    screenshot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'full_screenshot.png')
    driver.save_screenshot(screenshot_path)

    location = canvas.location
    size = canvas.size
    x, y = int(location['x']), int(location['y'])
    width, height = int(size['width']), int(size['height'])

    image = Image.open(screenshot_path)
    captcha_image = image.crop((x, y, x + width, y + height))
    save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
    captcha_image.save(save_path)
    print(f"Canvas 驗證碼已儲存至 {save_path}")

    with open(save_path, 'rb') as f:
        img_bytes = f.read()

    res = ocr.classification(img_bytes)
    return res

def button_event():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)

    driver.get("https://web085004.adm.ncyu.edu.tw/NewSite/Login.aspx?Language=zh-TW")

    # 嘗試用 WebDriverWait 等待並關閉彈窗（XPath 與 CSS Selector 雙重保險）
    try:
        wait = WebDriverWait(driver, 3)
        # 優先用 XPath 定位
        close_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '/html/body/div[6]/div[1]/button')
        ))
        close_btn.click()
        print("已用 XPath 成功關閉通知彈窗")
    except:
        try:
            # 再用 CSS Selector 嘗試
            close_btn = WebDriverWait(driver, 2).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'body > div:nth-child(7) > div.ui-dialog-titlebar.ui-corner-all.ui-widget-header.ui-helper-clearfix.ui-draggable-handle > button')
            ))
            close_btn.click()
            print("已用 CSS Selector 成功關閉通知彈窗")
        except:
            print("未偵測到通知彈窗，繼續執行")

    # 等驗證碼 canvas 出現後，再進行後續動作
    time.sleep(1)
    account = driver.find_element(By.NAME, "TbxAccountId")
    ssid = sid.get()
    account.send_keys(ssid)
    password = driver.find_element(By.NAME, "TbxPassword")
    sspw = spw.get()
    password.send_keys(sspw)

    # 擷取並辨識 canvas 驗證碼
    res = take_canvas_screenshot(driver, "captchaCanvas", "captcha_canvas.png")
    driver.find_element(By.NAME, "TbxCaptcha").send_keys(res)

    # 按「預登入」按鈕
    driver.find_element(By.NAME, "BtnPreLogin").click()

    # 如果需要選擇身份就選「學生」
    try:
        select_element = driver.find_element(By.ID, "DdlIdentitySelector")
        select = Select(select_element)
        time.sleep(2)
        select.select_by_visible_text("學生(" + ssid + ")")
        driver.find_element(By.XPATH, '//button[text()="登入"]').click()
    except:
        pass

    # 自動導航到教學意見調查並填寫
    time.sleep(2)
    driver.find_element(By.NAME, "BtnMenu").click()
    time.sleep(2)
    driver.find_element(By.LINK_TEXT, "教學意見調查作業").click()
    time.sleep(2)

    driver.switch_to.frame("application-frame-main")
    driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_BtnEntAns").click()
    time.sleep(2)
    driver.switch_to.default_content()
    driver.switch_to.frame("application-frame-main")
    driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_BtnSure").click()

    for _ in range(1, 50):
        # 計算題目數量
        flag = 1
        for i in range(1, 40):
            try:
                driver.find_element(By.ID, f"ctl00_ContentPlaceHolder1_RBAns{i}_0")
                flag += 1
            except:
                break

        # 填寫選定的滿意度
        for i in range(1, flag):
            driver.find_element(By.ID, f"ctl00_ContentPlaceHolder1_RBAns{i}_{degree}").click()

        driver.find_element(By.NAME, "ctl00$ContentPlaceHolder1$BtnSave").click()
        driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_BtnEntAns").click()
        driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_BtnSure").click()

    driver.quit()

def choose():  # 取得滿意度選項
    global degree
    degree = choice.get()

# GUI 介面設定
win = tk.Tk()
win.geometry("350x200")
win.title("Teaching_evaluation_auto_fill")
sid = tk.StringVar()
spw = tk.StringVar()

tk.Label(win, text="請輸入學號").grid(row=0, column=1, padx=10, pady=5)
tk.Label(win, text="請輸入密碼").grid(row=1, column=1, padx=10, pady=5)

tk.Entry(win, textvariable=sid).grid(row=0, column=2, padx=5, pady=5)
tk.Entry(win, textvariable=spw, show='*').grid(row=1, column=2, padx=5, pady=5)

choice = tk.StringVar()
tk.Label(win, text="請選擇滿意度").grid(row=3, column=2, padx=5, pady=5)
for idx, text in enumerate(["非常同意","同意","普通","不同意","非常不同意"]):
    tk.Radiobutton(win, text=text, variable=choice, value=str(idx), command=choose).grid(row=4+idx//3, column=1+idx%3, pady=5)

tk.Button(win, text="開始填寫", command=button_event).grid(row=6, column=2, pady=10)
win.mainloop()
