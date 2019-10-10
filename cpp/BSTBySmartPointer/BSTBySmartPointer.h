#include <utility>
#include <assert.h>
#include <iostream>
#include <memory>


using namespace std;
template<typename T>
class Tree {

    struct Node {
        T value;
        unique_ptr<Node> left {nullptr};
        unique_ptr<Node> right{nullptr};

        Node(const T& value): value(value) {}
    };

    public: 
        void insert(const T& value) {
            return insert(root_, value);
       } 

        bool Delete(const T& value) {
            return Delete(root_, value);
        }


        void printT() {
            printT(root_.get());
            cout << endl;
        }
    private:
        unique_ptr<Node> root_{nullptr};

        void insert(unique_ptr<Node>& node, const T& value) {
                
            if( !node ){
                node = make_unique<Node>(value);
            } else {
                value < node->value
                ? insert( node->left, value)
                : insert( node->right,value);
            } 

        }

        Node* successor(Node * node) {
            if ( node && node->right ) {
                node = node->right.get();
                while ( node->left ) {
                    node = node->left.get();
                }
                return node;
            }
            return nullptr;
        }
        

        // node can't be null as prerequisite
        bool Delete(unique_ptr<Node>& node, const T& value) {
            if ( !node ) {
                return false;
            }
          

            if ( value == node->value) {
                if ( node->left == nullptr) {
                    node = move(node->right);
                } else if ( node->right == nullptr) {
                    node = move(node->left);
                } else {
                    // we have two children: 
                    auto p = successor(node.get());
                    assert(p!=nullptr);
                    auto tmp = p->value;
                    Delete(node,p->value);
                    node->value = tmp;
                }
                return true;
            }
            
            if ( value < node->value ) {
                return Delete(node->left, value);
            } else {
                return Delete(node->right,value);
            }

        }

        void printT(Node* node) {
            if (!node) return;

            if ( node->left) {
                printT(node->left.get());
            }

            cout <<  node->value << " ";

            if (node->right) {
                printT(node->right.get());
            }
        }

};
