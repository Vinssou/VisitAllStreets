#!/usr/bin/python3

#command line : simpleGraphTraversal.py  -i test-city.csv -s A

import csv
import getopt
import sys
import copy
import random


class Node:
  def __init__(self, name):
    self.mName = name
    self.mStreets = set()
    self.mTempCost = 100*100

  def initTempCost(self):
    self.mTempCost = 100*100

  def __repr__(self):
    return self.mName

  def __str__(self):
    return self.mName

  def fullyVisted(self):
    for street in self.mStreets:
      if street.mVisitedCount == 0:
        return False
    return True

class Street:
  def __init__(self, name, node1, node2, cost):
    self.mName = name
    self.mNode1 = node1
    self.mNode2 = node2
    self.mCost = cost
    self.mVisitedCount = 0
    self.mNode1.mStreets.add(self)
    self.mNode2.mStreets.add(self)

  def __str__(self):
    return self.mName + " : " + self.mNode1.__str__() + " -> " + self.mNode2.__str__() + " cost  : " + str(self.mCost) + " visited  : " + str(self.mVisitedCount)

def sortStreet(street):
  return street.mVisitedCount #* 10000 + street.mCost

class City:
  def __init__(self):
    self.mIntersections = {}
    self.mStreets = {}

  def __str__(self):
    stringToPrint = ""
    for name, street in self.mStreets.items():
      stringToPrint = stringToPrint + street.__str__() + "\n"
    return stringToPrint + "\n";

  def fullyVisted(self):
    for name, street in self.mStreets.items():
      if street.mVisitedCount == 0:
        return False
    return True

  def initTempCost(self):
    for key, intersection in self.mIntersections.items():
      intersection.initTempCost()


def computeTravelCost(travel):
  totalCost = 0
  for inter in travel:
    totalCost = totalCost + inter[1]
  return totalCost

def main (argv):
  ############
  ### init ###
  ############
  inputfile = ''
  outputfile = ''
  streets = {}

  opts, args = getopt.getopt(argv,"hi:s:",["ifile=","start="])
  for opt, arg in opts:
    if opt == '-h':
      print ('solve.py -i <inputfile> -s <startNode>')
      sys.exit()
    elif opt in ("-i", "--ifile"):
      inputfile = arg
    elif opt in ("-s", "--start"):
      start = arg

  #############
  ### parse ###
  #############

  CityStreets = []
  nodeKeys = set()

  #print ('Parsing', inputfile, '...')
  with open (inputfile) as f:
    reader = csv.reader (f, delimiter=',')
    global totalLength
    totalLength = 0
    for row in reader:
      streetId = row[0]
      streets[streetId] = { 'node1': row[1], 'node2': row[2], 'len': int(row[3]), 'opt': row[4] }
      nodeKeys.add(row[1])
      nodeKeys.add(row[2])

      totalLength += streets[streetId]['len']
  print ('Street count:', len(streets))
  print ('Total length:', totalLength)
  print ('Parsing done.')


  #####################
  ### City creation ###
  #####################

  city = City()
  for nodeKey in nodeKeys:
    city.mIntersections[nodeKey] = Node(nodeKey)

  for streetId, data in streets.items():
    node1 = city.mIntersections[data['node1']]
    node2 = city.mIntersections[data['node2']]
    street = Street(streetId, node1, node2, data['len'])
    city.mStreets[streetId] = street
 
  
  #############
  ### solve ###
  #############
  print('Solving... for city : ')
  print(city)
 
  currentNode = city.mIntersections[start]
  travel = [(currentNode, 0)]

  IsBFS = False
  IsChineese = True
  if IsChineese:
    optimalTravel = runChineese(currentNode, city)
  else:
    if IsBFS:
      optimalTravel = runBFS(currentNode, travel, city)
    else:
      optimalTravel = run(currentNode, travel, city)

    # Warning the return travel could be from a copy of the city TODO fix that
    result = computeDikjstra(city.mIntersections[start], city.mIntersections[optimalTravel[-1][0].mName], city)
    print("Result from last point to start point: ", result)
  # done
  print ('Solving done. : ', optimalTravel, ' and cost ', computeTravelCost(optimalTravel) )



travelEndSize = 10000000000
minCost = 100000000

def run(currentNode, travel, city):

  global travelEndSize
  global minCost

  if False: #len(travel) == 2:
    print('------------------------')
    print('From NODE ---- >>>> ', currentNode)
    print('Traveled :: ', travel)
    print('City: \n', city)

  maxMulti = 2.0

  if len(travel)-1 > maxMulti * float(len(city.mStreets)):
    # print("Too long abort")
    return None

  #Check for the long street if the cost is too high
  if len(travel) >= travelEndSize:
    totalCost = computeTravelCost(travel)
    # print("Long enough ", len(travel) ," to test cost ", totalCost)
    if totalCost > minCost:
      # print("Too costly abort! best solution " + str(minCost) + " smallest number of intersection taken " + str(travelEndSize))
      # print('.' , end="", flush=True)
      return None

  if city.fullyVisted():
    totalCost = computeTravelCost(travel)
    print('\nSolution:   length ' + str(len(travel)) + " cost " + str(totalCost) + ' -> '+ str(travel), flush=True)
    if len(travel) < travelEndSize:
      travelEndSize = len(travel)
    if totalCost < minCost:
      minCost = totalCost

    return travel

  potentialStreets = []
  for street in currentNode.mStreets:
    # Valide street to take
    bConnectedStreet = False
    if street.mNode1 == currentNode:
      bConnectedStreet = True
    if street.mNode2 == currentNode:
      bConnectedStreet = True
    if not bConnectedStreet:
      continue

    potentialStreets.append(street)

  potentialStreets.sort(key=sortStreet)
  nextNode = None
  travels = []
  for index, street in enumerate(potentialStreets):
    if street.mVisitedCount < 2:
      if street.mNode1 == currentNode:
        nextNode = street.mNode2
      if street.mNode2 == currentNode:
        nextNode = street.mNode1

      # Don t copy last element
      if index+1 == len(potentialStreets):
        nextCity = city
        nextTravel = travel
      else:
        nextCity = copy.deepcopy(city)
        nextTravel = copy.deepcopy(travel)
      nextCityStreet = nextCity.mStreets[street.mName]
      nextCityNextNode = nextCity.mIntersections[nextNode.mName]
      nextCityStreet.mVisitedCount = nextCityStreet.mVisitedCount + 1
      nextTravel.append((nextCityNextNode, street.mCost))
      # input ('Press any key.')
      currentTravel = run(nextCityNextNode, nextTravel, nextCity)
      if currentTravel != None:
        travels.append(currentTravel)


  leastCost = 1000000000000
  leastTravel = None
  for thisTravel in travels:
    totalCost = computeTravelCost(thisTravel)
    if totalCost < leastCost:
      leastTravel = thisTravel
      leastCost = totalCost
  return leastTravel


def runBFS(currentNode, travel, city):

  theTravel = None

  if False: #len(travel) == 2:
    print('------------------------')
    print('From NODE ---- >>>> ', currentNode)
    print('Traveled :: ', travel)
    print('City: \n', city)

  maxMulti = 2.0

  queue = [(currentNode, travel, city)]

  while len(queue) != 0:
    
    currentTuple = queue.pop()
    currentNode = currentTuple[0]
    travel = currentTuple[1]
    city = currentTuple[2]


    print('START ', currentNode)
    print('Travel ', travel)

    if len(travel)-1 > maxMulti * float(len(city.mStreets)):
      #print("Too long abort")
      continue

    #Check for the long street if the cost is too high
    if len(travel) >= travelEndSize:
      totalCost = computeTravelCost(travel)
      print("Long enough ", len(travel) ," to test cost ", totalCost)
      if totalCost > minCost:
        #print("Too costly abort! best solution " + str(minCost) + " smallest number of intersection taken " + str(travelEndSize))
        print('.' , end="", flush=True)
        continue

    if city.fullyVisted():
      totalCost = computeTravelCost(travel)
      print('\nSolution:   length ' + str(len(travel)) + " cost " + str(totalCost) + ' -> '+ str(travel), flush=True)
      if len(travel) < travelEndSize:
        travelEndSize = len(travel)
      if totalCost < minCost:
        minCost = totalCos
        theTravel = travel
        continue

    potentialStreets = []
    for street in currentNode.mStreets:
      # Valide street to take
      bConnectedStreet = False
      if street.mNode1 == currentNode:
        bConnectedStreet = True
      if street.mNode2 == currentNode:
        bConnectedStreet = True
      if not bConnectedStreet:
        continue
      potentialStreets.append(street)

    potentialStreets.sort(key=sortStreet)
    nextNode = None
    travels = []
    for index, street in enumerate(potentialStreets):
      if street.mNode1 == currentNode:
        nextNode = street.mNode2
      if street.mNode2 == currentNode:
        nextNode = street.mNode1

      if street.mVisitedCount < 2:
        nextCity = copy.deepcopy(city)
        nextTravel = copy.deepcopy(travel)
        nextCityStreet = nextCity.mStreets[street.mName]
        nextCityNextNode = nextCity.mIntersections[nextNode.mName]
        nextCityStreet.mVisitedCount = nextCityStreet.mVisitedCount + 1
        nextTravel.append((nextCityNextNode, street.mCost))
        queue.append((nextCityNextNode, nextTravel, nextCity))
      
  return theTravel


def computeDikjstra(startNode, endNode, city):

  startNode.mTempCost = 0
  queue = [(startNode, [startNode])]

  theTravel = None
  while len(queue) != 0:
    
    currentTuple = queue.pop()
    currentNode = currentTuple[0]
    travel = currentTuple[1]

    #print('START ', currentNode)
    #print('END ', endNode)
    #print('Travel ', travel)
    if currentNode == endNode:
      # print("Found the end : ", currentNode, " - > ", endNode)
      theTravel = travel
    
    for street in currentNode.mStreets:
      nextNode = None
      if street.mNode1 == currentNode:
        nextNode = street.mNode2
      if street.mNode2 == currentNode:
        nextNode = street.mNode1
      if nextNode == None:
        continue

      nodeCost = street.mCost + currentNode.mTempCost
      if nodeCost < nextNode.mTempCost:
        nextNode.mTempCost = nodeCost
        if nodeCost <= endNode.mTempCost:
          nextTravel = copy.deepcopy(travel)
          nextTravel.append(nextNode)
          #input ('Press any key.')
          queue.append((nextNode, nextTravel))
      
  return theTravel

# 1 - Transformation en graphe eulérien : Ajoutez des arêtes artificielles au graphe pour le transformer en un graphe eulérien, en veillant à ce que chaque nœud ait un degré pair.
def computeOddIntersections(city):
  oddIntersections = []
  for key, intersection in city.mIntersections.items():
    if len(intersection.mStreets) % 2 == 1:
      oddIntersections.append(intersection)
  return oddIntersections


def findMinimumLinesWithZero(matrix):

  matrixSize = len(matrix)
  
  rowColumsZeros = [0 for _ in range(2*matrixSize)]
  
  for i in range(matrixSize):
    for j in range(matrixSize):
      if matrix[i][j] == 0:
        rowColumsZeros[i] = rowColumsZeros[i] + 1
        rowColumsZeros[matrixSize + j] = rowColumsZeros[matrixSize + j] + 1


  lines = [0 for _ in range(2*matrixSize)]
  while True:
    # Track more zero
    indexWithMoreZero = 0
    maxZero = 0
    for i in range(2*matrixSize):
      if rowColumsZeros[i] > maxZero:
        indexWithMoreZero = i
        maxZero = rowColumsZeros[i]

    if maxZero == 0:
      break
    # Keep track of the line
    lines[indexWithMoreZero] = 1
    rowColumsZeros[indexWithMoreZero] = 0

    # line is a row
    if indexWithMoreZero < matrixSize:
      for j in range(matrixSize):
        if matrix[indexWithMoreZero][j] == 0:
          rowColumsZeros[matrixSize + j] = rowColumsZeros[matrixSize + j] - 1
          assert(rowColumsZeros[matrixSize+ j] >= 0)
    else: # line is a column
      jIndex = indexWithMoreZero - matrixSize
      for i in range(matrixSize):
        if matrix[i][jIndex] == 0:
          rowColumsZeros[i] = rowColumsZeros[i] - 1
          assert(rowColumsZeros[matrixSize + j] >= 0)
    
  return lines


def reduceMatrix(matrix):

  matrixSize = len(matrix)
  for i in range(matrixSize):
    minCol = 100
    # Find min column
    for j in range(matrixSize):
      if matrix[i][j] < minCol:
        minCol = matrix[i][j]
    # Subtract min column
    for j in range(matrixSize):
      matrix[i][j] = matrix[i][j] - minCol
  # Same with row
  for j in range(matrixSize):
    minRow = 100
    # Find min column
    for i in range(matrixSize):
      if matrix[i][j] < minRow:
        minRow = matrix[i][j]
    # Subtract min column
    for i in range(matrixSize):
      matrix[i][j] = matrix[i][j] - minRow

  # print("Reduced Matrix : ")
  for i in range(matrixSize):
    print(matrix[i])

def augmentMatrix(matrix, lines):
  matrixSize = len(matrix)
  smallestNotOnLine = 10000
  smallI = -1
  smallJ = -1
  for i in range(matrixSize):
    for j in range(matrixSize):
      if lines[i] == 0 and lines[matrixSize + j] == 0:
        assert(matrix[i][j] != 0)
        if matrix[i][j] < smallestNotOnLine:
          smallestNotOnLine = matrix[i][j]
          smallI = i
          smallJ = j

  #print("Smallest no intersection: ", smallI, ", ",smallJ, " ->", smallestNotOnLine)
  #print("  Smallest value Not on lines: ", matrix[smallI][smallJ])
  for i in range(matrixSize):
    for j in range(matrixSize):
      # if not on a line
      if lines[i] == 0 and lines[matrixSize + j] == 0:
        matrix[i][j] = matrix[i][j] - smallestNotOnLine
      # if on a lines intersection
      elif lines[i] == 1 and lines[matrixSize + j] == 1:
        matrix[i][j] = matrix[i][j] + smallestNotOnLine
      assert(matrix[i][j] >= 0)

  #print("Augmented Matrix : ")
  #for i in range(matrixSize):
  #  print(matrix[i])


def computeSolution(matrix):
  matrixSize = len(matrix)
  associations = [[] for _ in range(matrixSize)]
  maxZeroCount = 0
  zeroCount = [0 for _ in range(matrixSize)]
  for i in range(matrixSize):
    zeroCount = 0
    for j in range(matrixSize):
      if matrix[i][j] == 0:
        zeroCount = zeroCount + 1
        associations[i].append(j)
    # If no 0 found
    if len(associations[i]) == 0:
      smallest = 100*100
      smallestIndex = -1
      for j in range(matrixSize):
        if matrix[i][j] < smallest:
          smallest = matrix[i][j]
          smallestIndex = j
      associations[i].append(smallestIndex)
    maxZeroCount = max(maxZeroCount, zeroCount)

  for step in range(matrixSize*matrixSize):
    solutionFound = True
    for i in range(matrixSize):
      for j in range(matrixSize):
        if i != j:
          if associations[i][0] == associations[j][0]:
            solutionFound = False
            # Swap i like in casino
            #print(i," == ",j," -> Swap")
            if len(associations[i]) > 1 and random.randrange(2) % 2 == 0:
              temp = associations[i][0]
              for k in range(len(associations[i]) -1):
                associations[i][k] = associations[i][k+1]
              associations[i][-1] = temp
            elif len(associations[j]) > 1:
              temp = associations[j][0]
              for k in range(len(associations[j]) -1):
                associations[j][k] = associations[j][k+1]
              associations[j][-1] = temp
    #print(step, " : ", associations)
    if solutionFound == True:
      break
  

  association = []
  for i in range(matrixSize):
    association.append(associations[i][0]) 

  if solutionFound == True:
    print("Solution found odd intersections to add in city : ", association)
  else:
    print("Solution not found after ", matrixSize*matrixSize, "iterations, odd intersections to add in city : ", association)
  return association

def hungarianAlgo(matrix):

  matrixSize = len(matrix)
  reduceMatrix(matrix)

  for _ in range(10):

    lines = findMinimumLinesWithZero(matrix)
    #print("Lines : ", lines)

    lineCount = 0
    for i in range(2*matrixSize):
      if lines[i] == 1:
        lineCount = lineCount + 1

    # We didn't find any solution keep going
    if lineCount < matrixSize:
      #print("No solution found need to augment the matrix")
      augmentMatrix(matrix, lines)
    else:
      print("End of Hungarian solution solvable...now try to find it...")
      return computeSolution(matrix)
    

def runHierholzerAlgo(startNode, city):
  
  travel =[(startNode, 0)]
  indexToInsert = 1
  while not city.fullyVisted():
    subTravel = []
    #print("Start Node: ", startNode)
    while not startNode.fullyVisted(): # Keep navigating while you can
      for street in startNode.mStreets:
        if street.mVisitedCount == 0:
          street.mVisitedCount = 1
          if street.mNode1 != startNode:
            #print("Connect to ", street.mNode1)
            assert(startNode == street.mNode2)
            startNode = street.mNode1
          else:
            #print("Connect to ", street.mNode2)
            assert(startNode == street.mNode1)
            startNode = street.mNode2
          subTravel.append((startNode, street.mCost))
          break

    #print(city)
    #print("subTravel ", subTravel)
    travel[indexToInsert:indexToInsert] = subTravel
    #print("travel ", travel)

    # Find a new node with vistied street, but not all
    for index, step in enumerate(travel):
      node, cost = step
      bHavFound = False
      for street in node.mStreets:
        if street.mVisitedCount == 0:
          startNode = node
          indexToInsert = index + 1
          #print(street, "  New start ", startNode, " -> ", indexToInsert)
          bHavFound = True
          break
      if bHavFound:
        break
        
  return travel
    

# 2 - Trouver un circuit eulérien : Utilisez un algorithme tel que l'algorithme de Hierholzer pour trouver un circuit eulérien dans le graphe, qui peut inclure des arêtes artificielles.
# 3 -Retirer les arêtes artificielles : Une fois que vous avez le circuit eulérien, retirez les arêtes artificielles du circuit.
def runChineese(startNode, city):

  oddIntersections = computeOddIntersections(city)
  oddIntersectionCount = len(oddIntersections)
  #print(oddIntersectionCount, " odd intersections :")
  #print(oddIntersections)
  assert(oddIntersectionCount % 2 == 0)
  matrixSize = oddIntersectionCount // 2

  
  oddMatrix = [[99 for i in range(matrixSize)] for j in range(matrixSize)]
  
  for i in range(matrixSize):
    for j in range(matrixSize):
      city.initTempCost()
      travel = computeDikjstra(oddIntersections[i], oddIntersections[matrixSize+j], city)
      #print("Final Travel : ", travel)
      shortestCost = travel[-1].mTempCost
      oddMatrix[i][j] = shortestCost

  print("Matrix : ")
  for i in range(matrixSize):
    print(oddMatrix[i])
  print("")
  originalMatrix = copy.deepcopy(oddMatrix)
  newStreets = hungarianAlgo(oddMatrix)
  print("Pseudo solution : ", newStreets)

  for curIndex, nextInter in enumerate(newStreets):
    name = "ArtStr" + oddIntersections[curIndex].mName + "2" + oddIntersections[nextInter].mName
    theStreet = Street(name, oddIntersections[curIndex], oddIntersections[nextInter], originalMatrix[curIndex][nextInter])
    city.mStreets[name] = theStreet

  print(city)

  totalCost = 0
  for key, street in city.mStreets.items():
    totalCost = totalCost + street.mCost

  print("Total cost : ", str(totalCost))

  return runHierholzerAlgo(startNode, city)
  


if __name__ == "__main__":
  main (sys.argv[1:])
  input ('Press any key.')
