import pyautogui
import time
from buttonAdvance import pressButtonAdvance, isThereButtonAdvance, pressMiddleScreen, pressNitroButton, scrollUp



def main():
    print("Spotlight automation script started.")
    time.sleep(4)
    # pressButtonAdvance(r"Assets\Images\spotlightEvent.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
    # pressButtonAdvance(r"Assets\Images\spotlightEvent.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
    # pressButtonAdvance(r"Assets\Images\spotlightPlayButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
    while True:
        pressButtonAdvance(r"Assets\Images\raceButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
        scrollUp(5)
        pressButtonAdvance(r"Assets\Images\saleenS1.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
        pressButtonAdvance(r"Assets\Images\play1.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
        for i in range(1, 120):
            pressButtonAdvance(r"Assets\Images\star.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
            if i % 8 == 0:
                pressNitroButton()
            time.sleep(1)
        pressButtonAdvance(r"Assets\Images\nextButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
        pressButtonAdvance(r"Assets\Images\nextButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
        pressButtonAdvance(r"Assets\Images\missoutButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
        pressMiddleScreen()
        pressButtonAdvance(r"Assets\Images\whiteNextButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
         


if __name__ == "__main__":
    main()
