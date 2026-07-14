import pyautogui
import time

def clickCoordinate(x: int, y: int, click_delay: float = 2.0, label: str = None):
    """Clicks the specified screen coordinates and sleeps for `click_delay` seconds."""
    if label:
        print(f"Clicking {label} at ({x}, {y})")
    else:
        print(f"Clicking coordinate ({x}, {y})")
    pyautogui.click(x, y)
    try:
        screen_w, screen_h = pyautogui.size()
        pyautogui.moveTo(screen_w - 5, screen_h // 2, duration=0.1)
    except Exception as e:
        print(f"Error moving mouse to right edge: {e}")
    time.sleep(click_delay)

def pressButtonAdvance(image_path: str, confidence: float = 0.7, retries: int = 3, delay: float = 1.0, ignorePanic: bool = True):
    """
    Tries to locate and click a button on the screen using the provided image.
    Retries up to `retries` times before raising an exception or continuing based on ignorePanic.
    """
    # Detect if we should search the bottom-right region
    lower_path = image_path.lower()
    is_bottom_right = any(name in lower_path for name in ["race", "skipButton", "nextbutton", "play1", "play2", "missoutbutton", "watchadpostracebutton", "backbutton"])
    
    if is_bottom_right:
        screen_w, screen_h = pyautogui.size()
        region = (1215, 715, screen_w - 1215, screen_h - 715)
    else:
        region = None

    for attempt in range(1, retries + 1):
        time.sleep(delay)
        try:
            button_location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=region, grayscale=True)
            if button_location:
                pyautogui.click(pyautogui.center(button_location))
                print(f"Button found and clicked on attempt {attempt} | {image_path}")
                
                # Move mouse to right edge after click to prevent hover highlights
                try:
                    screen_w, screen_h = pyautogui.size()
                    pyautogui.moveTo(screen_w - 5, screen_h // 2, duration=0.1)
                except Exception as e:
                    print(f"Error moving mouse to right edge: {e}")
                return True
        except Exception as e:
            if "ImageNotFoundException" not in type(e).__name__:
                print(f"Attempt {attempt}: Error occurred - {repr(e)}")
            
    if ignorePanic:
        return False
    else:
        raise RuntimeError(f"Button not found after {retries} attempts | {image_path} | Panicking!")
    

def isThereButtonAdvance(image_path: str, confidence: float = 0.7, retries: int = 3, delay: float = 1.0, ignorePanic: bool = True) -> bool:
    """
    Checks if a button exists on the screen using the provided image.
    Returns True if found, False otherwise.
    """
    # Detect if we should search the bottom-right region
    lower_path = image_path.lower()
    is_bottom_right = any(name in lower_path for name in ["race", "skipButton", "nextbutton", "play1", "play2", "missoutbutton", "watchadpostracebutton", "backbutton"])
    if is_bottom_right:
        screen_w, screen_h = pyautogui.size()
        region = (1215, 715, screen_w - 1215, screen_h - 715)
    else:
        region = None

    for attempt in range(1, retries + 1):
        time.sleep(delay)
        try:
            button_location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=region, grayscale=True)
            if button_location:
                print(f"Attempt {attempt}: Button found: {image_path}")
                return True
        except Exception as e:
            if "ImageNotFoundException" not in type(e).__name__:
                print(f"Error checking for button: {repr(e)}")
            
    if ignorePanic:
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