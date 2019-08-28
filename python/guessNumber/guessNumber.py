from collections import namedtuple

def strip(str):
    return str.strip()
    
def lower(str):
    return str.lower() 


def isValid(s, *transforms, validSet, predictor=None):
    """   This is to check if bypassing s through transforms, the result s is in validSet 
          Return  (resulting s, True) if successful
                  (None, False) if falied 
    """ 
    try: 
        for transform in transforms:
            s = transform(s)
    except ValueError: 
        return (None ,False)
    else:
        if validSet != None:
           return (s, True) if s in validSet else (None, False)             
        elif predictor != None:
           return (s, True) if predictor(s) else (None, False)             
        else:   
            return (s, True)           

def getInput(inputS,errS, *transforms, validSet, predictor=None): 
    while True:
        response = input(inputS)
        response, ok = isValid(response, *transforms, validSet=validSet, predictor=predictor)
        if ok: 
           break
        else:
           print(errS)
           
    return response           


def guess(max):
    Data = namedtuple('Data', ['value','valid'])
    min = Data(0,False)
    max = Data(max,False)
    times = 0
    num = min.value
    
    while max.value > min.value:
        times += 1 
        num = int((min.value + max.value)/2)
        while True:
            guidance = yield  print(str(num) + "?", end = " " )
            guidance, ok = isValid(guidance, str,lower,strip, validSet ={'l','c','h'})
            if ok: 
               break
            else:
               print("Error: Input can only be in 'l'|'h'|'c'|'L'|'H'|'C',please try again.")            
            
        if guidance == 'h':    
           max = Data(num,True)
        elif guidance == 'l':
           min = Data(num,True)
        elif guidance =='c':
            break
             
        if 1 == max.value - min.value:
           num = min.value if guidance == 'h' else max.value
           break
        elif max.valid and min.valid and 2 == max.value - min.value: 
            num = min.value +1
            break
        
    return (num, times)
      
   

def game(max):    
    sum = 0
    times = 0
    while True:
        num, numOfGuesses = yield from guess(max)
        sum += numOfGuesses
        times += 1
        
        print(f"Your number is {num}.")
        print(f"It took me {numOfGuesses} guesses.\nI averaged {sum/times:0.1f} per game for {times} game(s).")
        
        answer = getInput("Play again (y/n)? ",  "Error: Input must be a either Y/y or N/n, please try again.", \
                          str, lower, strip, validSet={'y','n'} )
                          
        if answer == 'y':
              continue
        elif answer == 'n':
              break;
       

def main():        
    
    prefix = ( "In this game, you think of a number from 1 through n and I will try to guess what it is. After each guess,\n" 
               "enter h if my guess is too high, l if too low, or c if correct." )
    print(prefix)
      
    num = getInput("Please input a positive number n: ", "Error: Input must be a positive integer, please try again.", \
                   int, validSet=None, predictor=lambda s : s>0 ) 
    g = game(num)
    next(g)
    
    while True:
       try: 
          g.send(input())
       except StopIteration:
          break
    
if __name__ == '__main__':   
	main()