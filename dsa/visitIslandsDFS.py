#!/usr/bin/env python3


def countIslandsDFS(matrix):
  rows = len(matrix)
  cols = len(matrix[0])
  totalIslands = 0

  for r in range(rows):
    for c in range(cols):
      if (matrix[r][c] == 1):
        totalIslands += 1
        print(f"r={r}, c={c}, total={totalIslands}")
        visitIslandDFS(matrix, r, c)

  return totalIslands;

def visitIslandDFS(matrix, r, c):
  rows = len(matrix)
  cols = len(matrix[0])
  if (r < 0 or r >= rows or c < 0 or c >= cols):
    return # invalid 
  
  if (matrix[r][c] == 0):
    return # water cell
  
  visitIslandDFS(matrix, r + 1, c) #lower
  visitIslandDFS(matrix, r - 1, c) #upper
  visitIslandDFS(matrix, r, c + 1) #right
  visitIslandDFS(matrix, r, c - 1) #left


def main():
  matrix = [
    [0,1,1,1,0],
    [0,0,0,1,1],
    [0,1,1,1,0],
    [0,1,1,0,0],
    [0,0,0,0,0]
  ]
  print(countIslandsDFS(matrix))

main()