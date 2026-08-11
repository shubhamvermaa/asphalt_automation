"""Car Hunt Main Automation Controller"""
import argparse, os, sys, time, winsound
from buttonAdvance import clickCoordinate, isThereButtonAdvance, pressLeftButton, pressMiddleScreen, pressSpaceButton
from coordinates import COORDINATES
from refuel import buyTicketDirectly, startAdsForTicketRefill, startRefuelAds
from selectCar import select_valid_car

class TeeLogger:
    def __init__(self, filename: str, mode: str = "a"):
        self.terminal, self.log = sys.stdout, open(filename, mode, encoding="utf-8", buffering=1)
    def write(self, message: str):
        self.terminal.write(message); self.log.write(message); self.log.flush()
    def flush(self):
        self.terminal.flush(); self.log.flush()

script_dir = os.path.dirname(os.path.abspath(__file__))
logger = TeeLogger(os.path.join(script_dir, "asphalt_automation.log"), mode="w")
sys.stdout = sys.stderr = logger

parser = argparse.ArgumentParser(description="Asphalt Car Hunt Automation Script")
parser.add_argument("--manage-missout", action="store_true")
parser.add_argument("--continue-from-play2", action="store_true")
args, _ = parser.parse_known_args()

BUY_TICKETS, WATCH_CREDITS_ADS, BUY_CAR_FUEL = True, False, False
MANAGE_MISSOUT_BUTTON, CONTINUE_FROM_PLAY2 = args.manage_missout, args.continue_from_play2

def waitForButton(image_path: str, confidence: float = 0.8, timeout: float = 120.0) -> bool:
    start_time = time.time()
    print(f"Waiting for {image_path}...")
    while True:
        if isThereButtonAdvance(image_path, confidence=confidence, retries=1, delay=0.1): return True
        if time.time() - start_time > timeout:
            print(f"❌ FATAL ERROR: Stuck waiting for {image_path} for > {int(timeout)}s.")
            try: winsound.Beep(1000, 1000)
            except Exception: print("\a", end="", flush=True)
            raise TimeoutError(f"Stuck waiting for {image_path} > {int(timeout)}s.")
        time.sleep(2)

def handleTicketsRefill():
    print("Handling ticket refills if necessary."); time.sleep(2)
    if isThereButtonAdvance(r"Assets\Images\refillTicketsBanner.png", confidence=0.7):
        if BUY_TICKETS:
            buyTicketDirectly(); waitForButton(r"Assets\Images\play2.png")
            clickCoordinate(*COORDINATES["play2_button"], label="play2_button")
        else: startAdsForTicketRefill()
        time.sleep(2)

def handleRace():
    print("Race started. Autopilot active (Nitro every 4s).")
    raceEnded, last_n, last_c, start_t = False, 0.0, 0.0, time.time()
    while not raceEnded:
        cur_t = time.time()
        if cur_t - last_n >= 4.0: pressSpaceButton(); last_n = time.time()
        if (cur_t - start_t >= 34.0) and (cur_t - last_c >= 3.0):
            pressLeftButton()
            raceEnded = isThereButtonAdvance(r"Assets\Images\nextButton.png", confidence=0.7, retries=1, delay=0.1)
            last_c = time.time()
        if cur_t - start_t > 120.0:
            print("❌ FATAL ERROR: Race autopilot running > 120s.")
            try: winsound.Beep(1000, 1000)
            except Exception: print("\a", end="", flush=True)
            raise TimeoutError("Race autopilot running > 120s.")
        time.sleep(0.2)

def handlePostRace():
    clickCoordinate(*COORDINATES["next_button"], label="first_next_button")
    print("Searching for second nextButton..."); waitForButton(r"Assets\Images\nextButton.png")
    clickCoordinate(*COORDINATES["next_button"], label="second_next_button")
    if WATCH_CREDITS_ADS:
        waitForButton(r"Assets\Images\watchAdPostRaceButton.png")
        clickCoordinate(*COORDINATES["watchAdPostRaceButton"], label="watchAdPostRaceButton"); time.sleep(2)
        waitForButton(r"Assets\Images\nextButton.png")
        clickCoordinate(*COORDINATES["next_button"], label="post_ad_first_next_button"); time.sleep(2)
        pressMiddleScreen(); time.sleep(2)
        waitForButton(r"Assets\Images\nextButton.png")
        clickCoordinate(*COORDINATES["next_button"], label="post_ad_second_next_button")
    else:
        if MANAGE_MISSOUT_BUTTON:
            print("Searching for miss out button..."); waitForButton(r"Assets\Images\missoutButton.png")
            clickCoordinate(*COORDINATES["missoutButton"], label="missoutButton")
        while not isThereButtonAdvance(r"Assets\Images\whiteNextButton.png", confidence=0.7, retries=1, delay=0.1):
            time.sleep(0.5); pressMiddleScreen(); time.sleep(0.5)
        time.sleep(1); clickCoordinate(*COORDINATES["white_next_button"], label="post_missout_white_next_button")

def main():
    print("Starting Car Hunt automation script...")
    if CONTINUE_FROM_PLAY2: print("Continuing execution directly from play2_button click...")
    for c in range(3, 0, -1): print(f"Starting in {c} seconds...", end="\r", flush=True); time.sleep(1)
    print("Starting now!     ")
    for i in range(1, 101):
        print(f"\n--- Race number: {i} ---")
        if not (i == 1 and CONTINUE_FROM_PLAY2):
            waitForButton(r"Assets\Images\raceButton.png")
            clickCoordinate(*COORDINATES["race_button"], label="race_button"); time.sleep(3)
            clickCoordinate(*COORDINATES["topCar"], label="topCar"); time.sleep(1)
            if not select_valid_car(target_class="B", minRank=3300, max_attempts=100):
                print("Warning: Could not find a valid car after 100 attempts!"); break
            time.sleep(1)
            if isThereButtonAdvance(r"Assets\Images\skipButton.png", confidence=0.7):
                clickCoordinate(*COORDINATES["carRefuelSkipButton"], label="carRefuelSkipButton")
                if BUY_CAR_FUEL: time.sleep(1); clickCoordinate(*COORDINATES["buyCarFuelButton"], label="buyCarFuelButton")
                else: startRefuelAds(); time.sleep(2)
                waitForButton(r"Assets\Images\play2.png")
        clickCoordinate(*COORDINATES["play2_button"], label="play2_button")
        handleTicketsRefill(); handleRace(); handlePostRace(); time.sleep(2)

if __name__ == "__main__": main()
