import pyautogui
import time
from buttonAdvance import pressButtonAdvance, isThereButtonAdvance


time.sleep(3)
print("running refule.py script")


def startRefuelAds():
    while True:
        try:
            time.sleep(2)
            pressButtonAdvance(r"Assets\Images\watchAdButton.png", confidence=0.6, retries=3, delay=1.0, ignorePanic=False)
            print("Ads found")
        except Exception:
            print("Error finding watchAd button")
            try:
                if pyautogui.locateOnScreen(r"Assets\Images\playButton.png", confidence=0.7):
                    print("Car Refuelled")
                    break
            except Exception:
                if isThereButtonAdvance(r"Assets\Images\refuelFastForwardBanner.png", confidence=0.7):
                    print("Buying Car fuel")
                    pressButtonAdvance(r"Assets\Images\skipCarRefuelButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
                    break
                print("More Fuel Ads are there")


def startAdsForTicketRefill():
    while True:
        time.sleep(1)
        try:
            watchAdButton = pyautogui.locateOnScreen(r"Assets\Images\refillTicketWatchAdButton.png", confidence=0.9)
            if watchAdButton:
                print("Ads found")
                pyautogui.click(pyautogui.center(watchAdButton))
        except Exception:
            print("Error finding Ticket watchAd button")
            if isThereButtonAdvance(r"Assets\Images\ticketFilledNotice.png", confidence=0.7):
                print("Ticket Refilled")
            if isThereButtonAdvance(r"Assets\Images\noMoreTicketAdsAvailable.png", confidence=0.7):
                print("Buying ticket")
                pressButtonAdvance(r"Assets\Images\buyTicketButton.png", confidence=0.9, retries=3, delay=1.0, ignorePanic=True)
            pressButtonAdvance(r"Assets\Images\backButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
            break
        print("More Tickets Ads are there")


def startRefuel():
    pressButtonAdvance(r"Assets\Images\skipButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
    startRefuelAds()


def searchEmptyFuel():
    for _ in range(20):
        time.sleep(1)
        try:
            pressButtonAdvance(r"Assets\Images\emptyFuelIcon.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
            print("empty fuel found")
            startRefuel()
            break
        except Exception as e:
            print(f"Empty fuel icon not found: {e}, scrolling further")
            # Scroll down to look for the fuel icon elsewhere on the screen
            screen_width, screen_height = pyautogui.size()
            center_x, center_y = screen_width // 2, screen_height // 2
            pyautogui.moveTo(center_x, center_y)
            pyautogui.scroll(-1200)
            time.sleep(0.5)
            pyautogui.moveTo(center_x, center_y)


# Brief delay to allow you to switch to the desired window

# garage = pyautogui.locateOnScreen(r"Assets\Images\garage.png", confidence=0.7)
# if garage:
#     center = pyautogui.center(garage)
#     pyautogui.moveTo(center)
#     pyautogui.click()
#     searchEmptyFuel()
# else:
#     print("Garage level screen image not found on the screen.")


# pyautogui.moveRel(100, 0, duration=0.2)  # Move mouse 100 pixels to the right

# daily_event_logo = pyautogui.locateOnScreen(r"Assets\Images\dailyEventsLogo.png")  # Ensure the file path is correct
# if daily_event_logo:
#     center = pyautogui.center(daily_event_logo)
#     pyautogui.moveTo(center)
#     pyautogui.click()
#     print("Daily event logo found and clicked.")
# else:
#     print("Daily event logo not found on the screen.")

