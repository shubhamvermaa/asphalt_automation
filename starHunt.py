import time
from buttonAdvance import pressButtonAdvance, isThereButtonAdvance, pressMiddleScreen, pressNitroButton

def handlePostRace():
    pressButtonAdvance(r"Assets\Images\nextButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
    pressButtonAdvance(r"Assets\Images\nextButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
    # watch ad or miss out
    time.sleep(2)
    pressButtonAdvance(r"Assets\Images\missoutButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
    time.sleep(3)
    pressMiddleScreen()
    time.sleep(2)
    pressButtonAdvance(r"Assets\Images\whiteNextButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
    time.sleep(2)


def buyTickets():
    if isThereButtonAdvance(r"Assets\Images\refillTicketsBanner.png", confidence=0.7):
        pressButtonAdvance(r"Assets\Images\buyTicketButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
        time.sleep(2)
        pressButtonAdvance(r"Assets\Images\redCrossButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
        pressButtonAdvance(r"Assets\Images\play1.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=True)
        time.sleep(2)


def handleRace():
    raceEnded, nitroCounter = False, 0
    while not raceEnded:
        raceEnded = isThereButtonAdvance(r"Assets\Images\nextButton.png", confidence=0.7)
        if nitroCounter % 8 == 0:
            # press space key for nitro
            pressNitroButton()
        nitroCounter += 1
        time.sleep(2)

def main():
    time.sleep(3)
    for i in range(1, 101):
        print(f"Race number: {i}")
        pressButtonAdvance(r"Assets\Images\raceButton.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=False)
        pressButtonAdvance(r"Assets\Images\play2.png", confidence=0.7, retries=3, delay=1.0, ignorePanic=False)
        buyTickets()
        handleRace()
        handlePostRace()

if __name__ == "__main__":
    main()
