"""classLine.py
Holds information about a line generated when a predator locks onto a prey
"""
import helpSimulate as hsm
import magicVariables as mv

class Line:

    def __init__(self, startPos, endPos):
        self.startPos = startPos
        self.endPos = endPos
    
