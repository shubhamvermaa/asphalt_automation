import time
from refuel import startRefuel, startAdsForTicketRefill
from buttonAdvance import pressButtonAdvance, isThereButtonAdvance, pressLeftButton, pressNitroButton, pressMiddleScreen, pressSpaceButton

def handleRefill():
    print("Handling refills if necessary.")
    time.sleep(2)
    # if isThereButtonAdvance(r"Assets\Images\skipButton.png", confidence=0.7):
    #     startRefuel()

    # if isThereButtonAdvance(r"Assets\Images\play1.png", confidence=0.7):
    #     pressButtonAdvance(r"Assets\Images\play1.png", confidence=0.7, retries=3, delay=1.0)

    if isThereButtonAdvance(r"Assets\Images\refillTicketsBanner.png", confidence=0.7):
        startAdsForTicketRefill()
        time.sleep(1)
        pressButtonAdvance(r"Assets\Images\play1.png", confidence=0.7, retries=3, delay=1.0)


def handleRace():
    raceEnded, nitroCounter = False, 0
    while not raceEnded:
        # if (isThereButtonAdvance(r"Assets\Images\nitroBottle.png", confidence=0.7)):
        # pressLeftButton()
        if nitroCounter % 1 == 0:
            # press space key for nitro
            pressSpaceButton()
            # pressNitroButton()
        nitroCounter += 1
        if nitroCounter % 2 == 0:
            raceEnded = isThereButtonAdvance(r"Assets\Images\NextButton.png", confidence=0.7)
        time.sleep(1)

def handlePostRace():
    pressButtonAdvance(r"Assets\Images\nextButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
    time.sleep(5)
    # pressMiddleScreen()
    pressButtonAdvance(r"Assets\Images\nextButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
    time.sleep(9)
    pressButtonAdvance(r"Assets\Images\watchAdPostRaceButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
    # pressButtonAdvance(r"Assets\Images\missoutButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
    # pressButtonAdvance(r"Assets\Images\whiteNextButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)

    adEnded = False
    while not adEnded:
        print("Searching for nextButton after Ad")
        adEnded = isThereButtonAdvance(r"Assets\Images\NextButton.png", confidence=0.7)
        time.sleep(2)
    pressButtonAdvance(r"Assets\Images\nextButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
    time.sleep(10)
    pressButtonAdvance(r"Assets\Images\nextButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)


def main():
    time.sleep(3)
    print("Starting SE Hunt automation script.")
    for i in range(1, 101):
        print(f"Race number: {i}")
        pressButtonAdvance(r"Assets\Images\nextButton.png", confidence=0.6, retries=3, delay=1.0, ignorePanic=True)
        time.sleep(3)
        pressButtonAdvance(r"Assets\Images\play1.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=False)
        handleRefill()
        handleRace()
        handlePostRace()


if __name__ == "__main__":
    main()
