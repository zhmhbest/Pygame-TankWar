import time



class Score:
    def __init__(self):
        pass

    def writeScore(score):
        with open("Score.txt", "a+") as file:
            string = ",".join((time.ctime(),str(score),"\n"))
            file.writelines(string)
            file.close()

        with open("Score.txt","r+") as file:
            highScore = file.readline()
            if score > int(highScore):
                file.seek(0)
                file.write(str(score))
            file.close()

    def getHighScore(file = open("Score.txt", "r")):
        highScore = file.readline()
        file.close()
        return int(highScore)
