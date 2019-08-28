import piece 
import chessBoard
import argparse


if __name__ == '__main__':  
    

    chess = chessBoard.ChessBoard()
    
    parser = argparse.ArgumentParser( description = ( "Find a list of all the potential board positions the given piece could advance to, \
                                                       with one move, from the given position, with the assumption there are no other pieces on the board" ))
                                                       
    parser.add_argument( '-piece', metavar = 'piece', type = str, choices=['KNIGHT','ROOK','QUEEN'], help = "Only support KNIGHT|ROOK|QUEEN."  )
    parser.add_argument( '-position', metavar = 'position', type = str, choices=[item for sublist in chess.getBoard() for item in sublist], \
                                                                       help = "position in the board that piece is on")
    res = parser.parse_args() 

    (row,col),ok  = chess.toIndex(res.position)
    
    if res.piece == "KNIGHT": 
       p = piece.Knight(row,col,chess)
    elif res.piece == "QUEEN":
       p = piece.Queen(row,col,chess)
    else :
       p = piece.Rook(row,col,chess)

    
    s = ", ".join(p.possibleMoves())
    print(f'"{s}"')
