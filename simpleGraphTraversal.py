#!/usr/bin/python3

import csv
import getopt
import sys
import copy


class Node:
  def __init__(self, name):
    self.mName = name
    self.mStreets = set()

  def __repr__(self):
    return self.mName
    
  def __str__(self):
    return self.mName

class Street:
  def __init__(self, name, node1, node2, cost):
    self.mName = name
    self.mNode1 = node1
    self.mNode2 = node2
    self.mCost = cost
    self.mVisitedCount = 0

  def __str__(self):
    return self.mName + " : " + self.mNode1.__str__() + " -> " + self.mNode2.__str__() + " : " + str(self.mVisitedCount)

def sortStreet(street):
  return street.mVisitedCount
  
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


def computeTravelCost(travel):
  totalCost = 0
  for inter in travel:
    totalCost = totalCost + inter[1]
  return totalCost

def main (argv):
  ############
  ### init ###
  ############
  print ('Init...')
  inputfile = ''
  outputfile = ''
  global streets
  streets = {}
  global start
  
  
  opts, args = getopt.getopt(argv,"hi:s:",["ifile=","start="])
  for opt, arg in opts:
    if opt == '-h':
      print ('solve.py -i <inputfile> -s <startNode>')
      sys.exit()
    elif opt in ("-i", "--ifile"):
      inputfile = arg
    elif opt in ("-s", "--start"):
      start = arg
  print ('Input file:', inputfile)
  print ('Start node:', start)
  print ('Init done.')
  print()

  #############
  ### parse ###
  #############

  CityStreets = []
  nodeKeys = set()
  
  print ('Parsing', inputfile, '...')
  with open (inputfile) as f:
    reader = csv.reader (f, delimiter=',')
    global totalLength
    totalLength = 0
    for row in reader:
      streetId = row[0]
      streets[streetId] = { 'node1': row[1], 'node2': row[2], 'len': int(row[3]), 'opt': row[4] }
      nodeKeys.add(row[1])
      nodeKeys.add(row[2])

      print('streetId: ', streetId)
      print('streets[streetId]: ', streets[streetId])
    
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
    print(streetId)
    print(data)
    node1 = city.mIntersections[data['node1']]
    node2 = city.mIntersections[data['node2']]
    street = Street(streetId, node1, node2, data['len'])
    city.mStreets[streetId] = street
    node1.mStreets.add(street)
    node2.mStreets.add(street)

  print(city)

  #############
  ### solve ###
  #############
  print ('Solving... for streets : ')
  print(streets)

  ### recurse!
  currentNode = city.mIntersections[start]
  travel = [(currentNode, 0)]
  optimalTravel = run(currentNode, travel, city)
  
  # done
  print ('Solving done. : ', optimalTravel, ' and cost ', computeTravelCost(optimalTravel) )

  
  
def run(currentNode, travel, city):

  if False: #len(travel) == 2:
    print('------------------------')
    print('From NODE ---- >>>> ', currentNode)
    print('Traveled :: ', travel)
    print('City: \n', city)

  maxMulti = 2.1

  if len(travel) > maxMulti * float(len(city.mStreets)):
    # print("Too long abort")
    return None

  if city.fullyVisted():
    print('Solution ' + str(travel) + " cost " + str(computeTravelCost(travel)), flush=True)
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
  for street in potentialStreets:

    bConnectedStreet = False
    if street.mNode1 == currentNode:
      nextNode = street.mNode2
      bConnectedStreet = True
    if street.mNode2 == currentNode:
      nextNode = street.mNode1
      bConnectedStreet = True
    if not bConnectedStreet:
      assert(False)
      continue

    # TODO don't copy last one
    nextCity = copy.deepcopy(city)
    nextTravel = copy.deepcopy(travel)
    nextStreet = nextCity.mStreets[street.mName]
    nextCityNextNode = nextCity.mIntersections[nextNode.mName]
    nextStreet.mVisitedCount = nextStreet.mVisitedCount + 1
    #print(street.mVisitedCount)
    nextTravel.append((nextCityNextNode, street.mCost))
    #print('City: \n', city)
    #print('Copy City: \n', nextCity)
    #input ('Press any key.')
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
  

if __name__ == "__main__":
  main (sys.argv[1:])
  input ('Press any key.')
