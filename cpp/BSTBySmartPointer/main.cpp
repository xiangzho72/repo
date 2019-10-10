#include "BSTBySmartPointer.h"


int main() {
   Tree<int> bst;

   bst.insert(50);
   bst.insert(30);
   bst.insert(20);
   bst.insert(40);
   bst.insert(70);
   bst.insert(60);
   bst.insert(80);
   bst.printT();

   bst.Delete(20);
   bst.printT();

   bst.Delete(30);
   bst.printT();

   bst.Delete(50);
   bst.printT();
}

