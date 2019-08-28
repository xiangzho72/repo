import operator

def checkInput(func):
    """ Decarator which check if row,col is a positive integar
    Returns:
        (None, False) if check failed, otherwise call func
    """
    def inner(chess,row,col):
        if  (True ==isinstance(row, int)) and (True==isinstance(col,int)) : 
            if row <0 or col <0 or row >= len(chess) or col >= len(chess):
                return None, False
        else: 
               return None, False
        return func(chess, row,col)
    return inner
        
class ChessBoard:
    def __init__(self):
        row = [ str(n) for n in range(1,9) ]
        col = [ s for s in 'abcdefgh']
        self._board = [ [c+r for c in col] for r in row ]
        
        index = [ n for n in range(8)]
        self._colMap = { key: value for key, value in zip(col, index)}
    
    def getCells(self):
        return [item for sublist in self._board for item in sublist]
        
    def toIndex(self, strPosition):
        """ Returns index of row,col from a string position
            for example:  strPosition='a2' should return:  ( 1, 0 ), True
        """
        if strPosition not in self.getCells():
            return (None, False)
        
        sCol, sRow = strPosition[0], strPosition[1]
        col = self._colMap[sCol]
        row = int(sRow) - 1
        return ((row, col), True)
    
    @checkInput
    def get(self, row, col):
        try : 
            a = self._board[row][col]
        except IndexError:
            return (None, False)
        else: 
            return (a, True)
        

    def getAtCol(self, col, start=None, end=None):
        try: 
            ret =  [row[col] for row in self._board[start:end]]    
        except IndexError as e:
            return (None, False)
        else: 
            return (ret, True)            
    
    def getAtRow(self, row, start=None, end=None):
         try: 
            ret =  self._board[row][start:end]    
         except IndexError as e:
            return (None, False)
         else: 
            return (ret, True)                
    
    def __len__(self):
        return len(self._board)



@checkInput    
def getCol(chess, row, col):
    """ Returns a list of cells on chess that with the same col as (row,col) except (row, col)
    """
    if row <0 or col < 0:
        return None,False    
    
    below, ok1 = chess.getAtCol(col,end=row)
    above, ok2 = chess.getAtCol(col,start=row+1)   
    if ok1 and ok2: 
        return below + above , True
    else:
        return None, False   
    
@checkInput        
def getRow(chess, row, col):
    """ Returns a list of cells on chess that with the same row as (row,col) except (row, col)
    """
    below, ok1 = chess.getAtRow(row,end=col)
    above, ok2 = chess.getAtRow(row,start=col+1)   
    if ok1 and ok2: 
        return below + above, True
    else:
        return None, False   
    
@checkInput
def getDiagonal(chess, row, col):
    """ Returns a list of cells on chess that on the diagnal direction as (row,col) except (row, col)
    """
    result =[]
    opers = [(operator.add, operator.add), \
             (operator.add, operator.sub), \
             (operator.sub, operator.add), \
             (operator.sub, operator.sub), ]
                                             
    for opera, operb in opers:
        for i in range(1,len(chess)):
            r, ok = chess.get(opera(row,i),operb(col,i))
            if ok: 
                result.append(r)
            else:
                break
    return result, True    


@checkInput
def getL(chess, row, col):
    """ Returns a list of cells on chess that a knight could run from (row,col) with one move
    """
    result =[] 
    leaps = [(1,2),(1,-2),(-1,2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1)]
    for x,y in leaps: 
        r, ok = chess.get(row+x, col+y)
        if ok:
           result.append(r)
    return result,True
	
