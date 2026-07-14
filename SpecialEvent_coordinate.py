import sys
import os
import time
import winsound

class TeeLogger:
    def __init__(self, filename, mode="a"):
        self.terminal = sys.stdout
        self.log = open(filename, mode, encoding="utf-8", buffering=1)
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()
    def flush(self):
        self.terminal.flush()
        self.log.flush()

# Set up logging to both stdout and asphalt_automation.log
script_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(script_dir, "asphalt_automation.log")
logger = TeeLogger(log_path, mode="w")
sys.stdout = logger
sys.stderr = logger

from refuel import startAdsForTicketRefill, buyTicketDirectly
from buttonAdvance import isThereButtonAdvance, pressMiddleScreen, pressSpaceButton, clickCoordinate
from coordinates import COORDINATES

BUY_TICKETS = True  # Set to True to buy tickets with tokens, False to watch ads for refills
WATCH_CREDITS_ADS = False  # Set to True to watch ads for credits after races

def waitForButton(image_path: str, confidence: float = 0.8, timeout: float = 120.0) -> bool:
    """
    Waits for a button to appear on the screen (checks every 2 seconds).
    If it takes longer than `timeout` seconds, it triggers a warning beep every second.
    Returns True when the button is found.
    """
    start_time = time.time()
    beep_interval = 1.0
    last_beep_time = 0
    
    print(f"Waiting for {image_path}...")
    while True:
        # Check if button exists on screen (fast check: retries=1, delay=0.1)
        if isThereButtonAdvance(image_path, confidence=confidence, retries=1, delay=0.1):
            return True
            
        elapsed = time.time() - start_time
        if elapsed > timeout:
            print(f"❌ FATAL ERROR: Stuck waiting for {image_path} for more than {int(timeout)}s. Terminating script.")
            try:
                winsound.Beep(1000, 1000) # Beep at 1000Hz for 1 second
            except Exception:
                print("\a", end="", flush=True) # Fallback bell
            raise TimeoutError(f"Stuck waiting for {image_path} for more than {int(timeout)}s.")
                
        time.sleep(2)

def handleRefill():
    print("Handling refills if necessary.")
    time.sleep(2)
    if isThereButtonAdvance(r"Assets\Images\refillTicketsBanner.png", confidence=0.7):
        if BUY_TICKETS: buyTicketDirectly()
        else: startAdsForTicketRefill()
        time.sleep(2)
        clickCoordinate(*COORDINATES["play1_button"], label="play1_button")

def handleRace():
    print("Race started. Autopilot active (Nitro every 5s).")
    raceEnded = False
    last_nitro_time = 0
    last_check_time = 0
    start_time = time.time()
    last_beep_time = 0

    while not raceEnded:
        current_time = time.time()

        # Press nitro every 5 seconds
        if current_time - last_nitro_time >= 5.0:
            pressSpaceButton()
            last_nitro_time = time.time()

        # Check if race ended every 3 seconds, but only after 30 seconds of race time have elapsed
        if (current_time - start_time >= 37.0) and (current_time - last_check_time >= 3.0):
            raceEnded = isThereButtonAdvance(r"Assets\Images\nextButton.png", confidence=0.7, retries=1, delay=0.1)
            last_check_time = time.time()

        # Stuck check if race is running for > 2 minutes
        elapsed = current_time - start_time
        if elapsed > 120.0:
            print(f"❌ FATAL ERROR: Race autopilot running for more than 120s. Terminating script.")
            try:
                winsound.Beep(1000, 1000)
            except Exception:
                print("\a", end="", flush=True)
            raise TimeoutError("Race autopilot running for more than 120s.")

        time.sleep(0.2)

def handlePostRace():
    # Search for first next button, click as soon as found
    # handle race confirmed this nextButton
    # print("Searching for first nextButton...")
    # waitForButton(r"Assets\Images\nextButton.png")
    clickCoordinate(*COORDINATES["next_button"], label="first_next_button")
    
    # Search for second next button, click as soon as found
    print("Searching for second nextButton...")
    waitForButton(r"Assets\Images\nextButton.png")
    clickCoordinate(*COORDINATES["next_button"], label="second_next_button")
    
    if WATCH_CREDITS_ADS:
        # Search for watch ad button, click as soon as found
        waitForButton(r"Assets\Images\watchAdPostRaceButton.png")
        clickCoordinate(*COORDINATES["watchAdPostRaceButton"], label="watchAdPostRaceButton")
        time.sleep(2)
        waitForButton(r"Assets\Images\nextButton.png")
        clickCoordinate(*COORDINATES["next_button"], label="post_ad_first_next_button")
        time.sleep(2)
        pressMiddleScreen()
        time.sleep(2)
        waitForButton(r"Assets\Images\nextButton.png")
        clickCoordinate(*COORDINATES["next_button"], label="post_ad_second_next_button")
    else:
        # Search for miss out button, click as soon as found
        print("Searching for miss out button...")
        waitForButton(r"Assets\Images\missoutButton.png")
        clickCoordinate(*COORDINATES["missoutButton"], label="missoutButton")
        time.sleep(2)
        pressMiddleScreen()
        time.sleep(2)
        waitForButton(r"Assets\Images\whiteNextButton.png")
        clickCoordinate(*COORDINATES["white_next_button"], label="post_missout_white_next_button")
         


def main():
    print("Starting SE Hunt automation script with coordinate-based clicks...")
    for count in range(4, 0, -1):
        print(f"Starting in {count} seconds...", end="\r", flush=True)
        time.sleep(1)
    print("Starting now!                                                 ")
    for i in range(1, 201):
        print(f"\n--- Race number: {i} ---")
        waitForButton(r"Assets\Images\nextButton.png")
        clickCoordinate(*COORDINATES["next_button"], label="pre_race_next_button")
        waitForButton(r"Assets\Images\play1.png")
        clickCoordinate(*COORDINATES["play1_button"], label="pre_race_play1_button")
        handleRefill()
        handleRace()
        handlePostRace()
        time.sleep(2)

if __name__ == "__main__":
    main()
