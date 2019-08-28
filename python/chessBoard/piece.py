import chessBoard

class Piece():
    def __init__(self,row,col,chess,*moves):
        if isinstance(row, int) and isinstance(col,int) and len(moves)>0 and isinstance(chess, chessBoard.ChessBoard):
            if row <0 or col <0 or row >= len(chess) or col >= len(chess):        
               raise ValueError
        else:
               raise ValueError 
        
        self._x = row
        self._y = col
        self._chess = chess
        self._moves = moves
    
    def possibleMoves(self):
        result = []
        for move in self._moves:
            res, ok = move(self._chess,self._x,self._y)
            if ok: 
                result.extend(res) 
            
        return result
    
class Queen(Piece):
    def __init__(self,row,col,chess):
        super().__init__(row,col,chess, chessBoard.getCol, chessBoard.getRow, chessBoard.getDiagonal)
        
class Rook(Piece):
    def __init__(self,row,col,chess):
        super().__init__(row,col,chess, chessBoard.getCol, chessBoard.getRow)
    
class Knight(Piece):
    def __init__(self,row,col,chess):
        super().__init__(row,col,chess, chessBoard.getL)
        
     
