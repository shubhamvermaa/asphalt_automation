import time
from refuel import startRefuel, startAdsForTicketRefill
from buttonAdvance import pressButtonAdvance, isThereButtonAdvance, pressMiddleScreen, pressNitroButton


def handleRefill():
    if isThereButtonAdvance(r"Assets\Images\skipButton.png", confidence=0.7):
        startRefuel()

    if isThereButtonAdvance(r"Assets\Images\playButton.png", confidence=0.7):
        pressButtonAdvance(r"Assets\Images\playButton.png", confidence=0.7, retries=3, delay=1.0)

    if isThereButtonAdvance(r"Assets\Images\refillTicketsBanner.png", confidence=0.7):
        startAdsForTicketRefill()
        time.sleep(1)
        pressButtonAdvance(r"Assets\Images\playButton.png", confidence=0.7, retries=3, delay=1.0)


def handleRace():
    raceEnded, nitroCounter = False, 0
    while not raceEnded:
        raceEnded = isThereButtonAdvance(r"Assets\Images\NextButton.png", confidence=0.7)
        if nitroCounter % 8 == 0:
            # press space key for nitro
            pressNitroButton()
        nitroCounter += 1
        time.sleep(1)


def handlePostRace():
    for action in [ pressButtonAdvance(r"Assets\Images\nextButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True),
                    pressButtonAdvance(r"Assets\Images\nextButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True),
                    pressButtonAdvance(r"Assets\Images\missoutButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True),
                    pressMiddleScreen,
                    pressButtonAdvance(r"Assets\Images\whiteNextButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
                   ]:
        action()
        time.sleep(2)


def main():
    time.sleep(3)
    print("Starting Car Hunt automation script.")
    for i in range(1, 101):
        print(f"Race number: {i}")
        pressButtonAdvance(r"Assets\Images\raceButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
        time.sleep(3)
        pressButtonAdvance(r"Assets\Images\formulaE.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
        handleRefill()
        pressButtonAdvance(r"Assets\Images\playButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
        handleRace()
        handlePostRace()


if __name__ == "__main__":
    main()
