import unittest

import chessBoard


class TestChessBoard(unittest.TestCase):
    def setUp(self):
        self.chess = chessBoard.ChessBoard()
        
    def test_toIndex(self):
        tests = { 'a1' : ((0,0),True ),
                  'g5' : ((4,6),True ),
                  'h8' : ((7,7),True ),
                  'h10': (None, False),
                  'i3':  (None, False),
                }
        for param, expRes in tests.items(): 
            res = self.chess.toIndex(param)
            self.assertEqual(res, expRes)

    def test_get(self):
        tests = { (0,0) : ('a1', True),
                  (4,6) : ('g5', True),
                  (7,7) : ('h8', True),
                  (-1,2): (None, False),
                  (1,-1): (None, False),
                  (1,10): (None, False),
                  (10,1): (None, False),
                  ('a',1):(None, False),
                  (1,'a'):(None, False),
                }
        for (row,col), expRes in tests.items(): 
            res = self.chess.get(row,col)
            self.assertEqual(res, expRes)
    
    def test_getCol(self):
        tests = {  (0,0) : (['a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8'], True),
                   (7,7) : (['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7'], True),
                   (0,7) : (['h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8'], True), 
                   (7,0) : (['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7'], True),
                   (1,8): (None,False),
                   (8,1): (None,False),
                   (-1,-1):(None,False),
                   (0,'a'):(None,False),
                   ('a',0):(None,False),
                } 
        for (row,col), expRes in tests.items(): 
            res = chessBoard.getCol(self.chess,row,col)
            self.assertEqual(res, expRes)

    def test_getRow(self):
        tests = {  (0,0) : (['b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1'], True),
                   (7,7) : (['a8', 'b8', 'c8', 'd8', 'e8', 'f8', 'g8'], True),
                   (0,7) : (['a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1'], True), 
                   (7,0) : (['b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8'], True),
                   (1,8): (None,False),
                   (8,1): (None,False),
                   (-1,-1):(None,False),
                   (0,'a'):(None,False),
                   ('a',0):(None,False),
                } 
        for (row,col), expRes in tests.items(): 
            res = chessBoard.getRow(self.chess,row,col)
            self.assertEqual(res, expRes)

    def test_getDiagonal(self):
        tests = {  (0,0) : (['b2', 'c3', 'd4', 'e5', 'f6', 'g7', 'h8'], True),
                   (7,7) : (['g7', 'f6', 'e5', 'd4', 'c3', 'b2', 'a1'], True),
                   (0,7) : (['g2', 'f3', 'e4', 'd5', 'c6', 'b7', 'a8'], True), 
                   (7,0) : (['b7', 'c6', 'd5', 'e4', 'f3', 'g2', 'h1'], True),
                   (2,3) : (['e4', 'f5', 'g6', 'h7', 'c4', 'b5', 'a6', 'e2', 'f1', 'c2', 'b1'],True),
                   (1,8): (None,False),
                   (8,1): (None,False),
                   (-1,-1):(None,False),
                   (0,'a'):(None,False),
                   ('a',0):(None,False),
                } 
        for (row,col), expRes in tests.items(): 
            res = chessBoard.getDiagonal(self.chess,row,col)
            self.assertEqual(res, expRes)

    def test_getL(self): 
        tests = {  (0,0) : (['c2', 'b3'], True),
                   (7,7) : (['f7', 'g6'], True),
                   (0,7) : (['f2', 'g3'], True), 
                   (7,0) : (['c7', 'b6'], True),
                   (2,3) : (['f4', 'b4', 'f2', 'b2', 'e5', 'c5', 'e1', 'c1'],True),
                   (1,8): (None,False),
                   (8,1): (None,False),
                   (-1,-1):(None,False),
                   (0,'a'):(None,False),
                   ('a',0):(None,False),
                } 
        for (row,col), expRes in tests.items(): 
            res = chessBoard.getL(self.chess,row,col)
            self.assertEqual(res, expRes)
            
if __name__ == '__main__':
    unittest.main()