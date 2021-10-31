import pygame
from copy import deepcopy
from random import choice, randint

class Game():
    def __init__(self):
        self.piecesTilePos = [[(-1,0),(-2,0),(0,0),(1,0)],  # 0 = I
                             [(0,-1),(-1,-1),(-1,0),(0,0)], # 1 = O
                             [(0,0),(0,-1),(0,1),(-1,0)],   # 2 = T
                             [(-1,0),(-1,1),(0,0),(0,-1)],  # 3 = Z
                             [(0,0),(-1,0),(0,1),(-1,-1)],  # 4 = S
                             [(0,0),(0,-1),(0,1),(-1,-1)],  # 5 = L
                             [(0,1),(0,-1),(0,0),(-1,1)]]   # 6 = J

        self.piecesList = [[pygame.Rect((x + amountTilesWidth // 2, y + 1), (1, 1)) for x, y in piece] for piece in self.piecesTilePos]
        self.pieceRect = pygame.Rect((0,0), (tileSize - 1, tileSize - 1))

        self.piece, self.nextPiece = deepcopy(choice(self.piecesList)), deepcopy(choice(self.piecesList))
        self.dirX = 0
        self.timerCount, self.timerSpeed, self.timerLimit = 0, 2, 50

        self.dx, self.rotate = 0, False

        self.mount = [[0 for tile in range(amountTilesWidth)] for tile in range(amountTilesHeight)]

        self.score, self.lines = 0, 0
        self.scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}

        #self.getColor = lambda : (randint(30,255), randint(30,255), randint(30,255))
        self.getColor = lambda : choice(((220, 10, 10),   # Red
                                         (50, 240, 0),   # Green
                                         (30, 30, 240),   # Blue
                                         (59, 240, 240),  # Cyan
                                         (200, 0, 240),  # Magenta
                                         (240, 240, 50),  # Yellow
                                         (240, 240, 240))) # white

        self.color, self.nextColor = self.getColor(), self.getColor()

        self.titleFont = pygame.font.Font("../Tetris/font/progresspixel-bold.ttf", 50)
        self.titleTetris = self.titleFont.render("TETRIS", False, (250, 100, 10))

        self.font = pygame.font.Font("../Tetris/font/progresspixel-bold.ttf", 35)
        self.titleScore = self.font.render("SCORE", False, (30, 240, 10))
        self.titleRecord = self.font.render("RECORD", False, (220, 10, 10))

        self.record = "0"

        self.titleRect = pygame.Rect((345, 10), (200, 75))
        self.previewRect = pygame.Rect((365, 100), (165, 135))
        self.scoreRect = pygame.Rect((345, 250), (200, 110))
        self.recordRect = pygame.Rect((345, 450), (200, 110))

        # Audio
        self.music = pygame.mixer.Sound("../Tetris/Audio/Tetris_theme.mp3")
        self.music.set_volume(0.04)
        self.music.play(loops = -1)

        self.hit = pygame.mixer.Sound("../Tetris/Audio/8_bit_slam.mp3")
        self.hit.set_volume(0.2)

        self.rotateSound = pygame.mixer.Sound("../Tetris/Audio/Turn.wav")
        self.rotateSound.set_volume(0.25)

        self.lineComplete = pygame.mixer.Sound("../Tetris/Audio/evolve.wav")
        self.lineComplete.set_volume(0.1)

        self.gameOverSound = pygame.mixer.Sound("../Tetris/Audio/game_over_arcade.wav")
        self.gameOverSound.set_volume(0.5)

    def drawRects(self):
        pygame.draw.rect(screen, "white", self.titleRect, 0, 12)
        pygame.draw.rect(screen, (50, 50, 70), self.previewRect, 0, 12)
        pygame.draw.rect(screen, (50, 70, 50), self.scoreRect, 0, 12)
        pygame.draw.rect(screen, (70, 50, 50), self.recordRect, 0, 12)

    def screenGrid(self):
        self.grid = [pygame.Rect((x * tileSize, y * tileSize), (tileSize, tileSize)) for x in range(amountTilesWidth) for y in range(amountTilesHeight)]
        [pygame.draw.rect(gameSurface, (50, 50, 70), rect, 1) for rect in self.grid]

    def drawPieces(self):
        for tile in range(4):
            self.pieceRect.x = self.piece[tile].x * tileSize
            self.pieceRect.y = self.piece[tile].y * tileSize
            pygame.draw.rect(gameSurface, self.color, self.pieceRect)

    def drawNextPiece(self):
        for tile in range(4):
            self.pieceRect.x = self.nextPiece[tile].x * tileSize + 290
            self.pieceRect.y = self.nextPiece[tile].y * tileSize + 120
            pygame.draw.rect(screen, self.nextColor, self.pieceRect)

    def movePieceX(self):
        self.oldPiece = deepcopy(self.piece)
        for tile in range(4):
            self.piece[tile].x += self.dirX

            # Limit Border
            if self.onLimitBorder():
                self.piece = deepcopy(self.oldPiece)
                break

    def movePieceY(self):
        # Timer
        self.timerCount += self.timerSpeed
        if self.timerCount > self.timerLimit:
            self.timerCount = 0

            # Move
            self.oldPiece = deepcopy(self.piece)
            for tile in range(4):
                self.piece[tile].y += 1
                if self.onLimitBorder():

                    # Build Mount
                    for tile in range(4):
                        self.mount[self.oldPiece[tile].y][self.oldPiece[tile].x] = self.color

                    # Next Piece
                    self.piece, self.color = self.nextPiece, self.nextColor

                    # Next Piece Preview
                    self.nextPiece, self.nextColor = deepcopy(choice(self.piecesList)), self.getColor()
                    self.timerLimit = 50

                    # Sound
                    self.hit.play()

                    break

    def rotatePiece(self):
        center = self.piece[0]
        oldPiece = deepcopy(self.piece)
        if self.rotate:
            for tile in range(4):
                x = self.piece[tile].y - center.y
                y = self.piece[tile].x - center.x
                self.piece[tile].x = center.x - x
                self.piece[tile].y = center.y + y
                if self.onLimitBorder():
                    self.piece = deepcopy(oldPiece)
                    break
            self.rotateSound.play()

    def onLimitBorder(self):
        for tile in range(4):
            if self.piece[tile].x < 0 or self.piece[tile].x > amountTilesWidth -1:
                return True
            elif self.piece[tile].y > amountTilesHeight - 1 or self.mount[self.piece[tile].y][self.piece[tile].x]:
                return True
        return False

    def drawMount(self):
        for y, column in enumerate(self.mount):
            for x, line in enumerate(column):
                if line:
                    self.pieceRect.x, self.pieceRect.y = x * tileSize, y * tileSize
                    pygame.draw.rect(gameSurface, line, self.pieceRect)

    def checkLines(self):
        line, self.lines = amountTilesHeight - 1, 0
        for column in range(amountTilesHeight - 1, -1, -1):
            count = 0
            for tile in range(amountTilesWidth):
                if self.mount[column][tile]:
                    count += 1
                self.mount[line][tile] = self.mount[column][tile]
            if count < amountTilesWidth:
                line -= 1
            else:
                self.timerCount += 3
                self.lines += 1
                self.lineComplete.play()


    def drawText(self):
        screen.blit(self.titleTetris, (350, 0))
        screen.blit(self.titleScore, (380, 250))
        screen.blit(self.font.render(str(self.score), False, (230, 230, 230)), (380, 295))
        screen.blit(self.titleRecord, (365, 450))
        screen.blit(self.font.render(self.record, False, pygame.Color("gold")), (365, 495))

    def computeScore(self):
        self.score += self.scores[self.lines]

    def delayForFullLines(self):
        for line in range(self.lines):
            pygame.time.wait(200)

    def getRecord(self):
        try:
            with open("record") as f:
                return f.readline()
        except:
            with open("record", "w") as f:
                f.write("0")

    def saveRecord(self, record, score):
        save = max(int(record), score)
        with open("record", "w") as f:
            f.write(str(save))

    def gameOver(self):
        for tile in range(amountTilesWidth):
            if self.mount[0][tile]:
                # Sound
                self.gameOverSound.play()
                # Set Record
                self.saveRecord(self.record, self.score)
                # Reset
                self.mount = [[0 for tile in range(amountTilesWidth)] for tile in range(amountTilesHeight)]
                self.timerCount, self.timerSpeed, self.timerLimit = 0, 1, 50
                self.score = 0
                # Game Over Animation
                for rect in self.grid:
                    pygame.draw.rect(gameSurface, self.getColor(), rect)
                    screen.blit(gameSurface, (20, 20))
                    pygame.display.flip()
                    clock.tick(200)
                
    def run(self):
        self.drawRects()
        self.screenGrid()
        self.getColor()
        self.drawNextPiece()
        self.drawPieces()
        self.movePieceY()
        self.drawMount()
        self.checkLines()
        self.delayForFullLines()
        self.computeScore()
        self.drawText()
        self.record = self.getRecord()
        self.gameOver()


if __name__ == "__main__":
    pygame.init()

    amountTilesWidth = 10
    amountTilesHeight = 20
    tileSize = 32

    screenResolution = (550, 680)
    gameResolution = (amountTilesWidth * tileSize, amountTilesHeight * tileSize)

    screen = pygame.display.set_mode(screenResolution)
    pygame.display.set_caption("Tetris by Eclizanto")
    gameSurface = pygame.Surface(gameResolution)

    screenBackground = pygame.image.load("../Tetris/images/Skyscrapers_background_ 1.jpg").convert()
    screenBackground = pygame.transform.scale(screenBackground, screenResolution)

    gameBackground = pygame.image.load("../Tetris/images/Skyscrapers_background_ 2.jpg").convert()
    gameBackground = pygame.transform.scale(gameBackground, (gameResolution))

    clock = pygame.time.Clock()
    FPS = 60

    game = Game()

    while True:
        screen.blit(screenBackground, (0,0))
        screen.blit(gameSurface, (20, 20))
        gameSurface.blit(gameBackground, (0, 0))

        game.run()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.dirX = -1
                    game.movePieceX()
                if event.key == pygame.K_RIGHT:
                    game.dirX = 1
                    game.movePieceX()
                if event.key == pygame.K_DOWN:
                    game.timerLimit = 3
                if event.key == pygame.K_UP:
                    game.rotate = True
                    game.rotatePiece()

        pygame.display.flip()
        clock.tick(FPS)