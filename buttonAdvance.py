import pyautogui
import time

def pressButtonAdvance(image_path: str, confidence: float = 0.7, retries: int = 3, delay: float = 1.0, ignorePanic: bool = True):
    """
    Tries to locate and click a button on the screen using the provided image.
    Retries up to `retries` times before raising an exception or continuing based on ignorePanic.
    """
    moveMouseToLeftEdge(delay=0.5)  # Move mouse to left edge before searching for the button
    for attempt in range(1, retries + 1):
        time.sleep(delay)
        try:
            button_location = pyautogui.locateOnScreen(image_path, confidence=confidence, grayscale=True)
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
    

def isThereButtonAdvance(image_path: str, confidence: float = 0.7, retries: int = 3, delay: float = 1.0, ignorePanic: bool = True) -> bool:
    """
    Checks if a button exists on the screen using the provided image.
    Returns True if found, False otherwise.
    """
    moveMouseToLeftEdge(delay=0.5)
    for attempt in range(1, retries + 1):
        time.sleep(delay)
        try:
            button_location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if button_location:
                print(f"Attempt {attempt}: Button found: {image_path}")
                return True
            else:
                print(f"Attempt {attempt}: Button not found: {image_path}")
        except Exception as e:
            print(f"Error checking for button: {e}")
    if ignorePanic:
        print(f"Button not found after {retries} attempts | {image_path} | Continuing without panicking.")
        return False
    else:
        raise RuntimeError(f"Button not found after {retries} attempts | {image_path} | Panicking!")
    

def pressMiddleScreen():
    time.sleep(1)
    screen_width, screen_height = pyautogui.size()

    middle_x = screen_width // 2
    middle_y = screen_height // 2

    print(f"Clicking at the middle of the screen: ({middle_x}, {middle_y})")
    pyautogui.click(middle_x, middle_y)

def pressLeftButton():
    time.sleep(1)
    pyautogui.press('left')

def pressSpaceButton():
    time.sleep(1)
    pyautogui.press('space')

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


def moveMouseToLeftEdge(delay: float = 1.0, y: int = None, margin: int = 0, duration: float = 0.2):
    """
    Move the mouse cursor to the left edge of the screen.

    Parameters:
    - delay: seconds to wait before moving the cursor (default: 1.0)
    - y: optional vertical coordinate to move to; if None uses vertical center
    - margin: pixels from the left edge (0 = exact edge)
    - duration: move duration in seconds (used by pyautogui.moveTo)

    Returns the final (x, y) position on success, or None on error.
    """
    time.sleep(delay)
    try:
        screen_width, screen_height = pyautogui.size()

        # clamp margin and y to valid screen coordinates
        target_x = max(0, min(margin, screen_width - 1))
        if y is None:
            target_y = screen_height // 2
        else:
            target_y = max(0, min(y, screen_height - 1))

        print(f"Moving mouse to left edge at ({target_x}, {target_y})")
        pyautogui.moveTo(target_x, target_y, duration=duration)
        return (target_x, target_y)
    except Exception as e:
        print(f"Error moving mouse to left edge: {e}")
        return None