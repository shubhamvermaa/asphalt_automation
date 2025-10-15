import pyautogui
import time
from buttonAdvance import pressButtonAdvance, isThereButtonAdvance, pressMiddleScreen, pressNitroButton, scrollUp



def main():
    print("Spotlight automation script started.")
    time.sleep(3)
    # pressButtonAdvance(r"Assets\Images\spotlightEvent.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
    # pressButtonAdvance(r"Assets\Images\spotlightEvent.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
    # pressButtonAdvance(r"Assets\Images\spotlightPlayButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
    while True:
        pressButtonAdvance(r"Assets\Images\raceButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=False)
        time.sleep(2)
        scrollUp(4)
        time.sleep(2)
        pressButtonAdvance(r"Assets\Images\Cars\saleenS1.png", confidence=0.8, retries=3, delay=1.0, ignorePanic=False)
        time.sleep(2)
        pressButtonAdvance(r"Assets\Images\play1.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=False)
        while not isThereButtonAdvance(r"Assets\Images\nextButton.png", confidence=0.7):
            pressButtonAdvance(r"Assets\Images\star.png", confidence=0.8, retries=1, delay=1.0, ignorePanic=True)
            time.sleep(0.5)
            pressButtonAdvance(r"Assets\Images\star.png", confidence=0.7, retries=1, delay=1.0, ignorePanic=True)
            time.sleep(0.5)
            # pressButtonAdvance(r"Assets\Images\star.png", confidence=0.6, retries=1, delay=1.0, ignorePanic=True)
            # time.sleep(0.5)
            pressNitroButton()
        pressButtonAdvance(r"Assets\Images\nextButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=False)
        time.sleep(2)
        pressButtonAdvance(r"Assets\Images\nextButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=False)
        time.sleep(4)
        pressButtonAdvance(r"Assets\Images\missoutButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=False)
        time.sleep(3)
        pressMiddleScreen()
        time.sleep(2)
        pressButtonAdvance(r"Assets\Images\backButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=False)
         


if __name__ == "__main__":
    main()
