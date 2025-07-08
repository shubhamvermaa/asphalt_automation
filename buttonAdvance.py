import pyautogui
import time

def pressButtonAdvance(image_path: str, confidence: float = 0.7, retries: int = 3, delay: float = 1.0, ignorePanic: bool = True):
    """
    Tries to locate and click a button on the screen using the provided image.
    Retries up to `retries` times before raising an exception or continuing based on ignorePanic.
    """
    for attempt in range(1, retries + 1):
        time.sleep(delay)
        try:
            button_location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if button_location:
                pyautogui.click(pyautogui.center(button_location))
                print(f"Button found and clicked on attempt {attempt} | {image_path}")
                return True
            else:
                print(f"Attempt {attempt}: Button not found.")
        except Exception as e:
            print(f"Attempt {attempt}: Error occurred - {e}")
    if ignorePanic:
        print(f"Button not found after {retries} attempts | {image_path} | Continuing without panicking.")
        return False
    else:
        raise RuntimeError(f"Button not found after {retries} attempts | {image_path} | Panicking!")
    

def isThereButtonAdvance(image_path: str, confidence: float = 0.7) -> bool:
    """
    Checks if a button exists on the screen using the provided image.
    Returns True if found, False otherwise.
    """
    try:
        button_location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if button_location:
            print(f"Button found: {image_path}")
            return True
        else:
            print(f"Button not found: {image_path}")
            return False
    except Exception as e:
        print(f"Error checking for button: {e}")
        return False
    

def pressMiddleScreen():
    time.sleep(1)
    screen_width, screen_height = pyautogui.size()

    middle_x = screen_width // 2
    middle_y = screen_height // 2

    print(f"Clicking at the middle of the screen: ({middle_x}, {middle_y})")
    pyautogui.click(middle_x, middle_y)


def pressNitroButton():
    time.sleep(1)
    try:
        nitroBar = pyautogui.locateOnScreen(r"Assets\Images\nitroBar.png", confidence=0.4)
        if nitroBar:
            print("Nitro bar found! Pressing space.")
            pyautogui.press('space')
        else:
            print("Nitro bar not found.")
    except Exception as e:
        print(f"An error occurred while trying to locate the nitro bar: {e}")


def scrollUp(times: int = 1):
    """
    Scrolls the screen up a specified number of times.
    """
    for i in range(times):
        time.sleep(1)
        pyautogui.scroll(1000)  # Positive value scrolls up
        print(f"Scrolled up {i + 1} times.")

def scrollDown(times: int = 1):
    """
    Scrolls the screen down a specified number of times.
    """
    for i in range(times):
        time.sleep(1)
        pyautogui.scroll(-1000)  # Negative value scrolls down
        print(f"Scrolled down {i + 1} times.")