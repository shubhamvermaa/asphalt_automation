import pyautogui
import time
import winsound
from buttonAdvance import pressButtonAdvance, isThereButtonAdvance, clickCoordinate
from coordinates import COORDINATES
time.sleep(3)

def _play_alarm():
    """Plays an auditory alert using winsound or console bell fallback."""
    try:
        winsound.Beep(1000, 1000)
    except Exception:
        print("\a", end="", flush=True)


def _wait_for_refuel_ad_to_finish(timeout=120):
    """Waits for the refuel ad to complete by scanning screen indicators or timing out."""
    print("Waiting for refuel ad to finish...")
    time.sleep(20)
    ad_start = time.time()

    while True:
        # When ad finishes, we should see watchAdButton, play2, or refuelFastForwardBanner
        if (isThereButtonAdvance(r"Assets\Images\refuelWatchAdButton.png", confidence=0.6, retries=1, delay=0.0) or 
            isThereButtonAdvance(r"Assets\Images\play2.png", confidence=0.7, retries=1, delay=0.0) or 
            isThereButtonAdvance(r"Assets\Images\refuelFastForwardBanner.png", confidence=0.7, retries=1, delay=0.0)):
            print("Ad finished. Returned to refuel screen.")
            break

        elapsed = time.time() - ad_start
        if elapsed > timeout:
            print(f"❌ FATAL ERROR: Refuel ad stuck for more than {timeout}s. Terminating script.")
            _play_alarm()
            raise TimeoutError(f"Refuel ad stuck for more than {timeout}s.")

        time.sleep(2)


def _handle_post_refuel_status(is_buying_allowed=False):
    """Checks car refuel status and handles fast-forward buying if allowed."""
    if isThereButtonAdvance(r"Assets\Images\play2.png", confidence=0.7):
        print("Car Refuelled")
    if is_buying_allowed and isThereButtonAdvance(r"Assets\Images\refuelFastForwardBanner.png", confidence=0.7):
        print("Buying Car fuel (Fast Forward)...")
        pressButtonAdvance(r"Assets\Images\skipCarRefuelButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
    print("No more fuel options, exiting refuel loop.")


def startRefuelAds():
    """Scans and watches refuel ads in a loop until finished or no more ads are available."""
    # When car refuel happens, we automatically go back to lobby
    isBuyingAllowed = False

    while True:
        try:
            time.sleep(2)
            if isThereButtonAdvance(r"Assets\Images\refuelWatchAdButton.png", confidence=0.6):
                print("Refuel Ad found.")
                clickCoordinate(*COORDINATES["carRefuelWatchAdButton"], label="carRefuelWatchAdButton")
                _wait_for_refuel_ad_to_finish()
            else:
                print("No refuel ad found. Exiting refuel loop.")
                _handle_post_refuel_status(isBuyingAllowed)
                break
        except Exception as e:
            if isinstance(e, TimeoutError):
                raise
            print(f"Refuel watchAd button error: {e}")
            _handle_post_refuel_status(isBuyingAllowed)
            break


def startAdsForTicketRefill():
    while True:
        try:
            time.sleep(1)
            if isThereButtonAdvance(r"Assets\Images\watchAdButton.png", confidence=0.9):
                print("Ads found.")
                clickCoordinate(*COORDINATES["ticketWatchAdButton"], label="ticketWatchAdButton")
                time.sleep(10) # Initial sleep for ad load
                print("Waiting for ad to finish...")
                ad_start_time = time.time()
                while True:
                    if (isThereButtonAdvance(r"Assets\Images\watchAdButton.png", confidence=0.8, retries=1, delay=0.0) or 
                        isThereButtonAdvance(r"Assets\Images\ticketFilledNotice.png", confidence=0.8, retries=1, delay=0.0) or
                        isThereButtonAdvance(r"Assets\Images\noMoreTicketAdsAvailable.png", confidence=0.8, retries=1, delay=0.0) or
                        isThereButtonAdvance(r"Assets\Images\backButton.png", confidence=0.8, retries=1, delay=0.0)):
                        print("Ad finished. Returned to ticket refill screen.")
                        break
                    # Stuck check
                    elapsed = time.time() - ad_start_time
                    if elapsed > 120:
                        print(f"❌ FATAL ERROR: Ticket ad stuck for more than 120s. Terminating script.")
                        try:
                            winsound.Beep(1000, 1000) # Beep at 1000Hz for 1 second
                        except Exception:
                            print("\a", end="", flush=True)
                        raise TimeoutError("Ticket ad stuck for more than 120s.")
                    time.sleep(2)
                continue # Go check for another ad
            else:
                # If no button found, raise ImageNotFoundException to handle refill complete / exit
                raise pyautogui.ImageNotFoundException("watchAdButton not found")    
        except (pyautogui.ImageNotFoundException, Exception) as e:
            print(f"Ticket watch ad button not found/available: {e}")
            # Check if ticket was refilled
            if isThereButtonAdvance(r"Assets\Images\ticketFilledNotice.png", confidence=0.7):
                print("Ticket Refilled")
            if isThereButtonAdvance(r"Assets\Images\noMoreTicketAdsAvailable.png", confidence=0.7):
                print("No more ticket ads available. Buying ticket...")
                pressButtonAdvance(r"Assets\Images\buyTicketButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
            print("Going back to main screen...")
            clickCoordinate(*COORDINATES["back_button"], label="back_button")
            break


def buyTicketDirectly():
    """
    Directly buys a ticket using screen coordinates and goes back.
    """
    print("Buying ticket directly using coordinates...")
    clickCoordinate(*COORDINATES["buy_ticket_button"], label="buy_ticket_button")
    time.sleep(2)  # Delay for purchase to process
    print("Going back to main screen...")
    clickCoordinate(*COORDINATES["back_button"], label="back_button")




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

